"""
IDC 打赏服务
集成 LinuxDo Credit (EasyPay 兼容协议) 实现优先处理打赏
"""
import hashlib
import logging
import uuid
import httpx
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import IdcOrder, WaitingRoom
from app.services.settings import settings_service

logger = logging.getLogger(__name__)

GATEWAY_BASE = "https://credit.linux.do/epay"


class IdcPaymentService:
    """IDC 打赏服务类"""

    def _generate_sign(self, params: dict, secret: str) -> str:
        """
        按 EasyPay 签名算法生成签名

        1. 取所有非空字段（排除 sign、sign_type）
        2. 按 ASCII 升序拼成 k1=v1&k2=v2
        3. 末尾追加密钥: k1=v1&k2=v2{secret}
        4. MD5 取小写十六进制
        """
        filtered = {
            k: v for k, v in params.items()
            if v is not None and v != "" and k not in ("sign", "sign_type")
        }
        sorted_keys = sorted(filtered.keys())
        payload = "&".join(f"{k}={filtered[k]}" for k in sorted_keys)
        raw = f"{payload}{secret}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def _verify_sign(self, params: dict, secret: str) -> bool:
        """验证回调签名"""
        sign = params.get("sign", "")
        expected = self._generate_sign(params, secret)
        return sign == expected

    async def create_order(
        self,
        email: str,
        db_session: AsyncSession,
        site_url: str
    ) -> Dict[str, Any]:
        """
        创建 IDC 打赏订单，返回签名参数供前端浏览器直接提交表单到支付网关。
        不能由服务端代发请求，因为用户需要携带自己的 LinuxDo 登录 session 去认证。

        Args:
            email: 用户邮箱
            db_session: 数据库会话
            site_url: 站点 URL (如 https://dash.xpzsd.codes)

        Returns:
            {"success": bool, "gateway_url": str, "form_params": dict, "order_no": str, "error": str}
        """
        try:
            # 获取 IDC 配置
            idc_config = await settings_service.get_idc_config(db_session)
            if not idc_config["enabled"]:
                return {"success": False, "gateway_url": None, "form_params": None, "order_no": None, "error": "IDC 打赏未启用"}

            pid = idc_config["pid"]
            key = idc_config["key"]
            amount = idc_config["amount"]

            if not pid or not key:
                return {"success": False, "gateway_url": None, "form_params": None, "order_no": None, "error": "IDC 配置不完整，请联系管理员"}

            # 生成唯一订单号
            order_no = f"IDC{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"

            # 回调和返回 URL
            notify_url = f"{site_url.rstrip('/')}/redeem/idc/notify"
            return_url = f"{site_url.rstrip('/')}/redeem/idc/return"

            # 构建请求参数
            params = {
                "pid": pid,
                "type": "epay",
                "out_trade_no": order_no,
                "name": "优先处理打赏",
                "money": str(amount),
                "notify_url": notify_url,
                "return_url": return_url,
            }

            # 生成签名
            params["sign"] = self._generate_sign(params, key)
            params["sign_type"] = "MD5"

            # 保存订单到数据库
            order = IdcOrder(
                out_trade_no=order_no,
                email=email,
                amount=str(amount),
                status="pending"
            )
            db_session.add(order)
            await db_session.commit()

            gateway_url = f"{GATEWAY_BASE}/pay/submit.php"
            logger.info(f"IDC 订单已创建: {order_no}, email={email}, amount={amount}")

            return {
                "success": True,
                "gateway_url": gateway_url,
                "form_params": params,
                "order_no": order_no,
                "error": None
            }

        except Exception as e:
            logger.error(f"IDC 创建订单异常: {e}")
            await db_session.rollback()
            return {
                "success": False,
                "gateway_url": None,
                "form_params": None,
                "order_no": None,
                "error": f"创建订单异常: {str(e)}"
            }

    async def handle_notify(
        self,
        params: dict,
        db_session: AsyncSession
    ) -> str:
        """
        处理异步通知回调

        Args:
            params: 回调参数
            db_session: 数据库会话

        Returns:
            "success" 或 "fail"
        """
        try:
            # 获取配置
            idc_config = await settings_service.get_idc_config(db_session)
            key = idc_config["key"]

            # 验签
            if not self._verify_sign(params, key):
                logger.warning(f"IDC 回调验签失败: {params}")
                return "fail"

            trade_status = params.get("trade_status", "")
            out_trade_no = params.get("out_trade_no", "")
            trade_no = params.get("trade_no", "")

            if trade_status != "TRADE_SUCCESS":
                logger.warning(f"IDC 回调非成功状态: {trade_status}, order={out_trade_no}")
                return "fail"

            # 查找订单
            result = await db_session.execute(
                select(IdcOrder).where(IdcOrder.out_trade_no == out_trade_no)
            )
            order = result.scalar_one_or_none()

            if not order:
                logger.warning(f"IDC 回调订单不存在: {out_trade_no}")
                return "fail"

            if order.status == "paid":
                logger.info(f"IDC 订单已处理过: {out_trade_no}")
                return "success"

            # 更新订单状态
            order.status = "paid"
            order.trade_no = trade_no
            order.paid_at = datetime.utcnow()

            # 将候车室中该用户标记为优先
            wr_result = await db_session.execute(
                select(WaitingRoom).where(
                    WaitingRoom.email == order.email,
                    WaitingRoom.notified == False
                )
            )
            waiting_entry = wr_result.scalar_one_or_none()

            if waiting_entry:
                waiting_entry.is_priority = True
                waiting_entry.idc_order_no = out_trade_no
                logger.info(f"候车用户 {order.email} 已标记为优先")
            else:
                # 用户未在候车室，自动加入并标记为优先
                new_entry = WaitingRoom(
                    email=order.email,
                    notified=False,
                    is_priority=True,
                    idc_order_no=out_trade_no
                )
                db_session.add(new_entry)
                logger.info(f"用户 {order.email} 自动加入候车室并标记优先")

            await db_session.commit()
            logger.info(f"IDC 订单支付成功: {out_trade_no}, email={order.email}")
            return "success"

        except Exception as e:
            logger.error(f"IDC 回调处理异常: {e}")
            await db_session.rollback()
            return "fail"

    async def query_order(
        self,
        out_trade_no: str,
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """
        查询订单状态（本地数据库）

        Args:
            out_trade_no: 业务订单号
            db_session: 数据库会话

        Returns:
            {"success": bool, "status": str, "error": str}
        """
        try:
            result = await db_session.execute(
                select(IdcOrder).where(IdcOrder.out_trade_no == out_trade_no)
            )
            order = result.scalar_one_or_none()

            if not order:
                return {"success": False, "status": None, "error": "订单不存在"}

            return {
                "success": True,
                "status": order.status,
                "email": order.email,
                "amount": order.amount,
                "error": None
            }

        except Exception as e:
            logger.error(f"查询订单异常: {e}")
            return {"success": False, "status": None, "error": str(e)}

    async def query_order_remote(
        self,
        out_trade_no: str,
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """
        从 LinuxDo Credit 平台查询订单状态并同步本地

        Args:
            out_trade_no: 业务订单号
            db_session: 数据库会话

        Returns:
            {"success": bool, "status": str, "error": str}
        """
        try:
            idc_config = await settings_service.get_idc_config(db_session)
            pid = idc_config["pid"]
            key = idc_config["key"]

            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"{GATEWAY_BASE}/api.php",
                    params={
                        "act": "order",
                        "pid": pid,
                        "key": key,
                        "out_trade_no": out_trade_no
                    }
                )

                if resp.status_code == 404:
                    return {"success": False, "status": "not_found", "error": "订单不存在"}

                data = resp.json()
                remote_status = "paid" if data.get("status") == 1 else "pending"

                # 同步到本地
                if remote_status == "paid":
                    result = await db_session.execute(
                        select(IdcOrder).where(IdcOrder.out_trade_no == out_trade_no)
                    )
                    order = result.scalar_one_or_none()
                    if order and order.status != "paid":
                        order.status = "paid"
                        order.trade_no = data.get("trade_no", "")
                        order.paid_at = datetime.utcnow()

                        # 标记优先
                        wr_result = await db_session.execute(
                            select(WaitingRoom).where(
                                WaitingRoom.email == order.email,
                                WaitingRoom.notified == False
                            )
                        )
                        waiting_entry = wr_result.scalar_one_or_none()
                        if waiting_entry:
                            waiting_entry.is_priority = True
                            waiting_entry.idc_order_no = out_trade_no
                        else:
                            db_session.add(WaitingRoom(
                                email=order.email,
                                notified=False,
                                is_priority=True,
                                idc_order_no=out_trade_no
                            ))

                        await db_session.commit()
                        logger.info(f"IDC 远程查询同步: {out_trade_no} -> paid")

                return {"success": True, "status": remote_status, "error": None}

        except Exception as e:
            logger.error(f"IDC 远程查询异常: {e}")
            return {"success": False, "status": None, "error": str(e)}


# 全局实例
idc_payment_service = IdcPaymentService()
