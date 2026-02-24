"""
ChatGPT API 服务
用于调用 ChatGPT 后端 API,实现 Team 成员管理功能
"""
import asyncio
import logging
from typing import Optional, Dict, Any, List
from curl_cffi.requests import AsyncSession
from app.services.settings import settings_service
from sqlalchemy.ext.asyncio import AsyncSession as DBAsyncSession

logger = logging.getLogger(__name__)


class ChatGPTService:
    """ChatGPT API 服务类"""

    BASE_URL = "https://chatgpt.com/backend-api"

    # 重试配置
    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 2, 4]  # 指数退避: 1s, 2s, 4s

    def __init__(self):
        """初始化 ChatGPT API 服务"""
        self.proxy: Optional[str] = None

    @staticmethod
    def _is_proxy_error(error_text: str) -> bool:
        """判断是否为代理相关异常"""
        if not error_text:
            return False
        text = error_text.lower()
        proxy_signatures = [
            "proxy",
            "curl: (5)",
            "curl: (7)",
            "curl: (56)",
            "curl: (97)",
            "could not resolve proxy",
            "connection to proxy"
        ]
        return any(sig in text for sig in proxy_signatures)

    @staticmethod
    def _build_browser_headers(access_token: str) -> Dict[str, str]:
        """构建更接近浏览器环境的基础请求头,降低 403 拦截概率"""
        return {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Authorization": f"Bearer {access_token}",
            "OAI-Client-Version": "prod-eddc2f6ff65fee2d0d6439e379eab94fe3047f72",
            "OAI-Language": "zh-CN",
            "Origin": "https://chatgpt.com",
            "Referer": "https://chatgpt.com/admin/members",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/142.0.0.0 Safari/537.36"
            )
        }

    @staticmethod
    def _swap_socks_scheme(proxy: str) -> Optional[str]:
        """socks5 与 socks5h 协议互转"""
        value = (proxy or "").strip().lower()
        if value.startswith("socks5://"):
            return proxy.replace("socks5://", "socks5h://", 1)
        if value.startswith("socks5h://"):
            return proxy.replace("socks5h://", "socks5://", 1)
        return None

    async def _get_proxy_config(self, db_session: DBAsyncSession) -> Optional[str]:
        """
        获取代理配置
        优先级: 手动代理 > SS 订阅节点代理

        Args:
            db_session: 数据库会话

        Returns:
            代理地址,如果未启用则返回 None
        """
        proxy_config = await settings_service.get_proxy_config(db_session)
        if proxy_config["enabled"] and proxy_config["proxy"]:
            return proxy_config["proxy"]

        # 检查 ss-local 代理
        from app.services.proxy_manager import ss_local_manager
        if ss_local_manager.is_running and ss_local_manager.local_proxy_url:
            return ss_local_manager.local_proxy_url

        return None

    async def _create_session(
        self,
        db_session: DBAsyncSession,
        force_no_proxy: bool = False,
        proxy_override: Optional[str] = None
    ) -> AsyncSession:
        """
        创建 HTTP 会话

        Args:
            db_session: 数据库会话

        Returns:
            curl_cffi AsyncSession 实例
        """
        # 获取代理配置
        if proxy_override is not None:
            proxy = proxy_override
        else:
            proxy = None if force_no_proxy else await self._get_proxy_config(db_session)

        # 创建会话 (使用 chrome 浏览器指纹)
        session = AsyncSession(
            impersonate="chrome",
            proxies={"http": proxy, "https": proxy} if proxy else None,
            timeout=30
        )

        if force_no_proxy:
            logger.info("创建 HTTP 会话,代理: 强制关闭(直连兜底)")
        else:
            logger.info(f"创建 HTTP 会话,代理: {proxy if proxy else '未使用'}")
        return session

    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        json_data: Optional[Dict[str, Any]] = None,
        db_session: Optional[DBAsyncSession] = None
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求 (带重试机制)

        Args:
            method: HTTP 方法 (GET/POST/DELETE)
            url: 请求 URL
            headers: 请求头
            json_data: JSON 请求体
            db_session: 数据库会话

        Returns:
            响应数据字典,包含 success, status_code, data, error
        """
        # 重试循环 — 每次尝试都创建独立 session,避免复用失效连接
        for attempt in range(self.MAX_RETRIES):
            session = None
            try:
                session = await self._create_session(db_session)
                logger.info(f"发送请求: {method} {url} (尝试 {attempt + 1}/{self.MAX_RETRIES})")

                # 发送请求
                if method == "GET":
                    response = await session.get(url, headers=headers)
                elif method == "POST":
                    response = await session.post(url, headers=headers, json=json_data)
                elif method == "DELETE":
                    response = await session.delete(url, headers=headers, json=json_data)
                else:
                    raise ValueError(f"不支持的 HTTP 方法: {method}")

                status_code = response.status_code
                logger.info(f"响应状态码: {status_code}")

                # 2xx 成功
                if 200 <= status_code < 300:
                    try:
                        data = response.json()
                    except Exception:
                        data = {}

                    return {
                        "success": True,
                        "status_code": status_code,
                        "data": data,
                        "error": None
                    }

                # 429 频率限制 — 需要重试
                if status_code == 429:
                    logger.warning(f"频率限制 429,准备重试")
                    if attempt < self.MAX_RETRIES - 1:
                        delay = self.RETRY_DELAYS[attempt] * 2  # 429 等更久
                        logger.info(f"等待 {delay}s 后重试")
                        await asyncio.sleep(delay)
                        continue
                    return {
                        "success": False,
                        "status_code": 429,
                        "data": None,
                        "error": f"请求频率过高,已重试 {self.MAX_RETRIES} 次"
                    }

                # 401 Token 过期 — 不重试,但给出明确提示
                if status_code == 401:
                    logger.warning("Token 已过期或无效 (401)")
                    return {
                        "success": False,
                        "status_code": 401,
                        "data": None,
                        "error": "Token 已过期或无效,请重新导入"
                    }

                # 403 可能是 CloudFlare 反爬,重试
                if status_code == 403:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("detail", response.text)
                    except Exception:
                        error_msg = response.text
                    logger.warning(f"403 拦截 (尝试 {attempt + 1}/{self.MAX_RETRIES}): {error_msg}")
                    if attempt < self.MAX_RETRIES - 1:
                        delay = self.RETRY_DELAYS[attempt]
                        logger.info(f"等待 {delay}s 后重试")
                        await asyncio.sleep(delay)
                        continue

                    # 最后一次仍 403 时,尝试 socks5/socks5h 互转代理再补偿请求一次
                    if db_session is not None:
                        configured_proxy = await self._get_proxy_config(db_session)
                        alt_proxy = self._swap_socks_scheme(configured_proxy or "") if configured_proxy else None
                        if alt_proxy:
                            logger.warning(f"403 最终重试失败,尝试替代代理协议补偿请求: {alt_proxy}")
                            alt_session = None
                            try:
                                alt_session = await self._create_session(
                                    db_session,
                                    force_no_proxy=False,
                                    proxy_override=alt_proxy
                                )

                                if method == "GET":
                                    alt_response = await alt_session.get(url, headers=headers)
                                elif method == "POST":
                                    alt_response = await alt_session.post(url, headers=headers, json=json_data)
                                elif method == "DELETE":
                                    alt_response = await alt_session.delete(url, headers=headers, json=json_data)
                                else:
                                    raise ValueError(f"不支持的 HTTP 方法: {method}")

                                alt_status = alt_response.status_code
                                logger.info(f"替代代理协议补偿响应状态码: {alt_status}")

                                if 200 <= alt_status < 300:
                                    try:
                                        alt_data = alt_response.json()
                                    except Exception:
                                        alt_data = {}
                                    return {
                                        "success": True,
                                        "status_code": alt_status,
                                        "data": alt_data,
                                        "error": None
                                    }
                            except Exception as alt_error:
                                logger.error(f"替代代理协议补偿请求失败: {alt_error}")
                            finally:
                                if alt_session:
                                    try:
                                        await alt_session.close()
                                    except Exception:
                                        pass

                    return {
                        "success": False,
                        "status_code": 403,
                        "data": None,
                        "error": f"请求被拦截 (403),已重试 {self.MAX_RETRIES} 次: {error_msg}"
                    }

                # 其他 4xx 客户端错误 (不重试)
                if 400 <= status_code < 500:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("detail", response.text)
                    except Exception:
                        error_msg = response.text

                    logger.warning(f"客户端错误 {status_code}: {error_msg}")

                    return {
                        "success": False,
                        "status_code": status_code,
                        "data": None,
                        "error": f"HTTP {status_code}: {error_msg}"
                    }

                # 5xx 服务器错误 (需要重试)
                if status_code >= 500:
                    logger.warning(f"服务器错误 {status_code},准备重试")

                    if attempt < self.MAX_RETRIES - 1:
                        delay = self.RETRY_DELAYS[attempt]
                        logger.info(f"等待 {delay}s 后重试")
                        await asyncio.sleep(delay)
                        continue

                    return {
                        "success": False,
                        "status_code": status_code,
                        "data": None,
                        "error": f"服务器错误 {status_code},已重试 {self.MAX_RETRIES} 次"
                    }

            except asyncio.TimeoutError:
                logger.warning(f"请求超时 (尝试 {attempt + 1}/{self.MAX_RETRIES})")

                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAYS[attempt]
                    logger.info(f"等待 {delay}s 后重试")
                    await asyncio.sleep(delay)
                    continue

                return {
                    "success": False,
                    "status_code": 0,
                    "data": None,
                    "error": f"请求超时,已重试 {self.MAX_RETRIES} 次"
                }

            except Exception as e:
                logger.error(f"请求异常: {e}")

                # 代理异常时,在最终失败前自动尝试 socks5/socks5h 互转重试
                if (
                    attempt == self.MAX_RETRIES - 1
                    and db_session is not None
                    and self._is_proxy_error(str(e))
                ):
                    configured_proxy = await self._get_proxy_config(db_session)
                    if configured_proxy and (
                        configured_proxy.startswith("socks5://")
                        or configured_proxy.startswith("socks5h://")
                    ):
                        alt_proxy = (
                            configured_proxy.replace("socks5://", "socks5h://", 1)
                            if configured_proxy.startswith("socks5://")
                            else configured_proxy.replace("socks5h://", "socks5://", 1)
                        )
                        logger.warning(f"检测到代理异常,尝试替代代理协议: {alt_proxy}")
                        alt_session = None
                        try:
                            alt_session = await self._create_session(
                                db_session,
                                force_no_proxy=False,
                                proxy_override=alt_proxy
                            )

                            if method == "GET":
                                direct_response = await alt_session.get(url, headers=headers)
                            elif method == "POST":
                                direct_response = await alt_session.post(url, headers=headers, json=json_data)
                            elif method == "DELETE":
                                direct_response = await alt_session.delete(url, headers=headers, json=json_data)
                            else:
                                raise ValueError(f"不支持的 HTTP 方法: {method}")

                            direct_status_code = direct_response.status_code
                            logger.info(f"直连兜底响应状态码: {direct_status_code}")

                            if 200 <= direct_status_code < 300:
                                try:
                                    data = direct_response.json()
                                except Exception:
                                    data = {}

                                return {
                                    "success": True,
                                    "status_code": direct_status_code,
                                    "data": data,
                                    "error": None
                                }

                            try:
                                direct_error_data = direct_response.json()
                                direct_error_msg = direct_error_data.get("detail", direct_response.text)
                            except Exception:
                                direct_error_msg = direct_response.text

                            return {
                                "success": False,
                                "status_code": direct_status_code,
                                "data": None,
                                "error": f"代理异常且替代代理返回 HTTP {direct_status_code}: {direct_error_msg}"
                            }
                        except Exception as direct_error:
                            logger.error(f"替代代理兜底请求失败: {direct_error}")
                            return {
                                "success": False,
                                "status_code": 0,
                                "data": None,
                                "error": f"请求异常: {str(e)}; 替代代理兜底失败: {str(direct_error)}"
                            }
                        finally:
                            if alt_session:
                                try:
                                    await alt_session.close()
                                except Exception:
                                    pass

                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAYS[attempt]
                    logger.info(f"等待 {delay}s 后重试")
                    await asyncio.sleep(delay)
                    continue

                return {
                    "success": False,
                    "status_code": 0,
                    "data": None,
                    "error": f"请求异常: {str(e)}"
                }

            finally:
                if session:
                    try:
                        await session.close()
                    except Exception:
                        pass

        return {
            "success": False,
            "status_code": 0,
            "data": None,
            "error": "未知错误"
        }

    async def send_invite(
        self,
        access_token: str,
        account_id: str,
        email: str,
        db_session: DBAsyncSession
    ) -> Dict[str, Any]:
        """
        发送 Team 邀请

        Args:
            access_token: AT Token
            account_id: Account ID
            email: 邀请的邮箱地址
            db_session: 数据库会话

        Returns:
            结果字典,包含 success, status_code, error
        """
        url = f"{self.BASE_URL}/accounts/{account_id}/invites"

        headers = self._build_browser_headers(access_token)
        headers["Content-Type"] = "application/json"
        headers["chatgpt-account-id"] = account_id

        json_data = {
            "email_addresses": [email],
            "role": "standard-user",
            "resend_emails": True
        }

        logger.info(f"发送邀请: {email} -> Team {account_id}")

        result = await self._make_request("POST", url, headers, json_data, db_session)

        # 特殊处理 409 (用户已是成员)
        if result["status_code"] == 409:
            result["error"] = "用户已是该 Team 的成员"

        # 特殊处理 422 (Team 已满或邮箱格式错误)
        if result["status_code"] == 422:
            result["error"] = "Team 已满或邮箱格式错误"

        return result

    async def get_members(
        self,
        access_token: str,
        account_id: str,
        db_session: DBAsyncSession
    ) -> Dict[str, Any]:
        """
        获取 Team 成员列表

        Args:
            access_token: AT Token
            account_id: Account ID
            db_session: 数据库会话

        Returns:
            结果字典,包含 success, members (成员列表), total (总数), error
        """
        all_members = []
        offset = 0
        limit = 50

        while True:
            url = f"{self.BASE_URL}/accounts/{account_id}/users?limit={limit}&offset={offset}"

            headers = self._build_browser_headers(access_token)
            headers["chatgpt-account-id"] = account_id

            logger.info(f"获取成员列表: Team {account_id}, offset={offset}")

            result = await self._make_request("GET", url, headers, db_session=db_session)

            if not result["success"]:
                return {
                    "success": False,
                    "members": [],
                    "total": 0,
                    "error": result["error"]
                }

            # 解析响应
            data = result["data"]
            items = data.get("items", [])
            total = data.get("total", 0)

            all_members.extend(items)

            # 检查是否还有更多成员
            if len(all_members) >= total:
                break

            offset += limit

        logger.info(f"获取成员列表成功: 共 {len(all_members)} 个成员")

        return {
            "success": True,
            "members": all_members,
            "total": len(all_members),
            "error": None
        }

    async def get_invites(
        self,
        access_token: str,
        account_id: str,
        db_session: DBAsyncSession
    ) -> Dict[str, Any]:
        """
        获取 Team 待加入成员列表 (邀请列表)

        Args:
            access_token: AT Token
            account_id: Account ID
            db_session: 数据库会话

        Returns:
            结果字典,包含 success, items (邀请列表), total (总数), error
        """
        url = f"{self.BASE_URL}/accounts/{account_id}/invites"

        headers = self._build_browser_headers(access_token)
        headers["chatgpt-account-id"] = account_id

        logger.info(f"获取邀请列表: Team {account_id}")

        result = await self._make_request("GET", url, headers, db_session=db_session)

        if not result["success"]:
            return {
                "success": False,
                "items": [],
                "total": 0,
                "error": result["error"]
            }

        data = result["data"]
        items = data.get("items", [])
        total = data.get("total", 0)

        return {
            "success": True,
            "items": items,
            "total": total,
            "error": None
        }

    async def delete_invite(
        self,
        access_token: str,
        account_id: str,
        email: str,
        db_session: DBAsyncSession
    ) -> Dict[str, Any]:
        """
        撤回 Team 邀请

        Args:
            access_token: AT Token
            account_id: Account ID
            email: 邀请的邮箱地址
            db_session: 数据库会话

        Returns:
            结果字典,包含 success, status_code, error
        """
        url = f"{self.BASE_URL}/accounts/{account_id}/invites"

        headers = self._build_browser_headers(access_token)
        headers["Content-Type"] = "application/json"
        headers["chatgpt-account-id"] = account_id

        json_data = {
            "email_address": email
        }

        logger.info(f"撤回邀请: {email} from Team {account_id}")

        result = await self._make_request("DELETE", url, headers, json_data, db_session)

        return result

    async def delete_member(
        self,
        access_token: str,
        account_id: str,
        user_id: str,
        db_session: DBAsyncSession
    ) -> Dict[str, Any]:
        """
        删除 Team 成员

        Args:
            access_token: AT Token
            account_id: Account ID
            user_id: 用户 ID (格式: user-xxx)
            db_session: 数据库会话

        Returns:
            结果字典,包含 success, status_code, error
        """
        url = f"{self.BASE_URL}/accounts/{account_id}/users/{user_id}"

        headers = self._build_browser_headers(access_token)
        headers["chatgpt-account-id"] = account_id

        logger.info(f"删除成员: {user_id} from Team {account_id}")

        result = await self._make_request("DELETE", url, headers, db_session=db_session)

        # 特殊处理 403 (无权限删除 owner)
        if result["status_code"] == 403:
            result["error"] = "无权限删除该成员 (可能是 owner)"

        # 特殊处理 404 (用户不存在)
        if result["status_code"] == 404:
            result["error"] = "用户不存在"

        return result

    async def get_account_info(
        self,
        access_token: str,
        db_session: DBAsyncSession
    ) -> Dict[str, Any]:
        """
        获取 account-id 和订阅信息

        Args:
            access_token: AT Token
            db_session: 数据库会话

        Returns:
            结果字典,包含 success, accounts (账户列表), error
        """
        url = f"{self.BASE_URL}/accounts/check/v4-2023-04-27"

        headers = self._build_browser_headers(access_token)

        logger.info("获取 account-id 和订阅信息")

        result = await self._make_request("GET", url, headers, db_session=db_session)

        if not result["success"]:
            return {
                "success": False,
                "accounts": [],
                "error": result["error"]
            }

        # 解析响应
        data = result["data"]
        accounts_data = data.get("accounts", {})

        # 提取所有 Team 类型的账户
        team_accounts = []
        for account_id, account_info in accounts_data.items():
            account = account_info.get("account", {})
            entitlement = account_info.get("entitlement", {})

            # 只保留 Team 类型的账户
            if account.get("plan_type") == "team":
                team_accounts.append({
                    "account_id": account_id,
                    "name": account.get("name", ""),
                    "plan_type": account.get("plan_type", ""),
                    "subscription_plan": entitlement.get("subscription_plan", ""),
                    "expires_at": entitlement.get("expires_at", ""),
                    "has_active_subscription": entitlement.get("has_active_subscription", False)
                })

        logger.info(f"获取账户信息成功: 共 {len(team_accounts)} 个 Team 账户")

        return {
            "success": True,
            "accounts": team_accounts,
            "error": None
        }

    async def close(self):
        """兼容旧调用,现在每次请求自动关闭 session,无需手动调用"""
        pass


# 创建全局实例
chatgpt_service = ChatGPTService()
