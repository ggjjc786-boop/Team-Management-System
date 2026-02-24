"""LinuxDo OAuth 认证与用户积分相关服务。"""
import uuid
from datetime import datetime
from urllib.parse import urlencode

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import LinuxDoUser, PointTransaction, RedemptionCode, ShopOrder


class LinuxDoAuthService:
    """LinuxDo 登录、签到与积分商城服务。"""

    def build_authorize_url(self, base_url: str, state: str, oauth_config: dict | None = None) -> str:
        oauth_config = oauth_config or {}
        redirect_path = oauth_config.get("redirect_path") or settings.linuxdo_redirect_path
        redirect_uri = f"{base_url.rstrip('/')}{redirect_path}"
        query = urlencode(
            {
                "response_type": "code",
                "client_id": oauth_config.get("client_id") or settings.linuxdo_client_id,
                "redirect_uri": redirect_uri,
                "scope": oauth_config.get("scope") or settings.linuxdo_scope,
                "state": state,
            }
        )
        authorize_url = oauth_config.get("authorize_url") or settings.linuxdo_authorize_url
        return f"{authorize_url}?{query}"

    async def exchange_code_for_userinfo(self, code: str, base_url: str, oauth_config: dict | None = None) -> dict:
        oauth_config = oauth_config or {}
        redirect_path = oauth_config.get("redirect_path") or settings.linuxdo_redirect_path
        redirect_uri = f"{base_url.rstrip('/')}{redirect_path}"
        token_url = oauth_config.get("token_url") or settings.linuxdo_token_url
        userinfo_url = oauth_config.get("userinfo_url") or settings.linuxdo_userinfo_url
        client_id = oauth_config.get("client_id") or settings.linuxdo_client_id
        client_secret = oauth_config.get("client_secret") or settings.linuxdo_client_secret

        async with httpx.AsyncClient(timeout=15.0) as client:
            token_resp = await client.post(
                token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                },
                headers={"Accept": "application/json"},
            )
            token_resp.raise_for_status()
            token_data = token_resp.json()

            access_token = token_data.get("access_token")
            if not access_token:
                raise ValueError("LinuxDo OAuth 未返回 access_token")

            user_resp = await client.get(
                userinfo_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            )
            user_resp.raise_for_status()
            return user_resp.json()

    def _normalize_userinfo(self, raw: dict) -> dict:
        data = raw.get("user") if isinstance(raw.get("user"), dict) else raw

        linuxdo_user_id = (
            data.get("id")
            or data.get("user_id")
            or data.get("sub")
            or data.get("uid")
        )
        username = data.get("username") or data.get("name") or data.get("login")
        display_name = data.get("name") or data.get("display_name") or username
        email = data.get("email")
        avatar_url = data.get("avatar_template") or data.get("avatar_url")

        if not linuxdo_user_id or not username:
            raise ValueError("LinuxDo 用户信息不完整")

        return {
            "linuxdo_user_id": str(linuxdo_user_id),
            "username": str(username),
            "display_name": str(display_name) if display_name else str(username),
            "email": email,
            "avatar_url": avatar_url,
        }

    async def get_or_create_user(self, raw_userinfo: dict, db: AsyncSession) -> LinuxDoUser:
        profile = self._normalize_userinfo(raw_userinfo)

        result = await db.execute(
            select(LinuxDoUser).where(LinuxDoUser.linuxdo_user_id == profile["linuxdo_user_id"])
        )
        user = result.scalar_one_or_none()

        if not user:
            user = LinuxDoUser(
                linuxdo_user_id=profile["linuxdo_user_id"],
                username=profile["username"],
                display_name=profile["display_name"],
                email=profile["email"],
                avatar_url=profile["avatar_url"],
                points=0,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user

        user.username = profile["username"]
        user.display_name = profile["display_name"]
        user.email = profile["email"]
        user.avatar_url = profile["avatar_url"]
        await db.commit()
        await db.refresh(user)
        return user

    async def daily_sign_in(self, user_id: int, db: AsyncSession) -> dict:
        result = await db.execute(select(LinuxDoUser).where(LinuxDoUser.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return {"success": False, "error": "用户不存在"}

        now = datetime.now()
        if user.last_sign_in_at and user.last_sign_in_at.date() == now.date():
            return {"success": False, "error": "今天已经签到过了", "points": user.points}

        delta = int(settings.user_daily_signin_points)
        user.points += delta
        user.last_sign_in_at = now

        db.add(
            PointTransaction(
                user_id=user.id,
                change=delta,
                type="signin",
                description="每日签到",
            )
        )
        await db.commit()
        await db.refresh(user)

        return {
            "success": True,
            "message": f"签到成功，获得 {delta} 积分",
            "points": user.points,
            "gained": delta,
        }

    async def buy_shop_item(self, user_id: int, item_key: str, cost: int, db: AsyncSession) -> dict:
        user_result = await db.execute(select(LinuxDoUser).where(LinuxDoUser.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            return {"success": False, "error": "用户不存在"}

        if cost <= 0:
            return {"success": False, "error": "商品价格异常"}

        if user.points < cost:
            return {
                "success": False,
                "error": "积分不足",
                "points": user.points,
                "required": cost,
            }

        if item_key != "redeem_code":
            return {"success": False, "error": "该商品暂未开放"}

        code_result = await db.execute(
            select(RedemptionCode)
            .where(
                RedemptionCode.status == "unused",
                RedemptionCode.is_shop_sold == False,
            )
            .order_by(RedemptionCode.id.asc())
            .limit(1)
        )
        redemption_code = code_result.scalar_one_or_none()

        if not redemption_code:
            return {"success": False, "error": "商城库存不足，请稍后再试"}

        order_no = f"SHOP{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"

        user.points -= cost
        redemption_code.is_shop_sold = True
        redemption_code.shop_sold_to_user_id = user.id
        redemption_code.shop_sold_at = datetime.utcnow()

        order = ShopOrder(
            order_no=order_no,
            user_id=user.id,
            item_key=item_key,
            points_cost=cost,
            redemption_code_id=redemption_code.id,
            redemption_code=redemption_code.code,
            status="success",
        )
        db.add(order)
        db.add(
            PointTransaction(
                user_id=user.id,
                change=-cost,
                type="purchase",
                description=f"积分商城购买 {item_key}",
                related_order_no=order_no,
            )
        )

        await db.commit()
        await db.refresh(user)

        return {
            "success": True,
            "message": "购买成功",
            "order_no": order_no,
            "code": redemption_code.code,
            "cost": cost,
            "points": user.points,
        }


linuxdo_auth_service = LinuxDoAuthService()
