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
        self.session: Optional[AsyncSession] = None
        self.proxy: Optional[str] = None

    async def _get_proxy_config(self, db_session: DBAsyncSession) -> Optional[str]:
        """
        获取代理配置

        Args:
            db_session: 数据库会话

        Returns:
            代理地址,如果未启用则返回 None
        """
        proxy_config = await settings_service.get_proxy_config(db_session)
        if proxy_config["enabled"] and proxy_config["proxy"]:
            return proxy_config["proxy"]
        return None

    async def _create_session(self, db_session: DBAsyncSession) -> AsyncSession:
        """
        创建 HTTP 会话

        Args:
            db_session: 数据库会话

        Returns:
            curl_cffi AsyncSession 实例
        """
        # 获取代理配置
        proxy = await self._get_proxy_config(db_session)

        # 创建会话 (使用 chrome 浏览器指纹)
        session = AsyncSession(
            impersonate="chrome",
            proxies={"http": proxy, "https": proxy} if proxy else None,
            timeout=30
        )

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
        # 创建会话
        if not self.session:
            self.session = await self._create_session(db_session)

        # 重试循环
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"发送请求: {method} {url} (尝试 {attempt + 1}/{self.MAX_RETRIES})")

                # 发送请求
                if method == "GET":
                    response = await self.session.get(url, headers=headers)
                elif method == "POST":
                    response = await self.session.post(url, headers=headers, json=json_data)
                elif method == "DELETE":
                    response = await self.session.delete(url, headers=headers, json=json_data)
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

                # 4xx 客户端错误 (不重试)
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
                        "error": error_msg
                    }

                # 5xx 服务器错误 (需要重试)
                if status_code >= 500:
                    logger.warning(f"服务器错误 {status_code},准备重试")

                    # 如果不是最后一次尝试,等待后重试
                    if attempt < self.MAX_RETRIES - 1:
                        delay = self.RETRY_DELAYS[attempt]
                        logger.info(f"等待 {delay}s 后重试")
                        await asyncio.sleep(delay)
                        continue

                    # 最后一次尝试失败
                    return {
                        "success": False,
                        "status_code": status_code,
                        "data": None,
                        "error": f"服务器错误 {status_code},已重试 {self.MAX_RETRIES} 次"
                    }

            except asyncio.TimeoutError:
                logger.warning(f"请求超时 (尝试 {attempt + 1}/{self.MAX_RETRIES})")

                # 如果不是最后一次尝试,等待后重试
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAYS[attempt]
                    logger.info(f"等待 {delay}s 后重试")
                    await asyncio.sleep(delay)
                    continue

                # 最后一次尝试失败
                return {
                    "success": False,
                    "status_code": 0,
                    "data": None,
                    "error": f"请求超时,已重试 {self.MAX_RETRIES} 次"
                }

            except Exception as e:
                logger.error(f"请求异常: {e}")

                # 如果不是最后一次尝试,等待后重试
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAYS[attempt]
                    logger.info(f"等待 {delay}s 后重试")
                    await asyncio.sleep(delay)
                    continue

                # 最后一次尝试失败
                return {
                    "success": False,
                    "status_code": 0,
                    "data": None,
                    "error": f"请求异常: {str(e)}"
                }

        # 不应该到达这里
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

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "chatgpt-account-id": account_id
        }

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

            headers = {
                "Authorization": f"Bearer {access_token}"
            }

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

        headers = {
            "Authorization": f"Bearer {access_token}",
            "chatgpt-account-id": account_id
        }

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

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "chatgpt-account-id": account_id
        }

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

        headers = {
            "Authorization": f"Bearer {access_token}",
            "chatgpt-account-id": account_id
        }

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

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

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
        """关闭 HTTP 会话"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("HTTP 会话已关闭")


# 创建全局实例
chatgpt_service = ChatGPTService()
