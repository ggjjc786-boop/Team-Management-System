"""LinuxDo 登录、每日签到与积分商城路由。"""
import logging
import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies.auth import require_linuxdo_user
from app.models import LinuxDoUser, PointTransaction, ShopOrder
from app.services.linuxdo_auth import linuxdo_auth_service
from app.services.settings import settings_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["linuxdo"])


@router.get("/user/auth/login")
async def linuxdo_login(request: Request, db: AsyncSession = Depends(get_db)):
    """跳转到 LinuxDo OAuth 授权页。"""
    from app.services.settings import settings_service

    oauth_config = await settings_service.get_linuxdo_oauth_config(db)

    if not oauth_config.get("enabled", False):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LinuxDo 登录未启用")

    if not oauth_config.get("client_id") or not oauth_config.get("client_secret"):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LinuxDo OAuth 配置不完整")

    state = secrets.token_urlsafe(24)
    request.session["linuxdo_oauth_state"] = state

    base_url = str(request.base_url).rstrip("/")
    authorize_url = linuxdo_auth_service.build_authorize_url(base_url, state, oauth_config)
    return RedirectResponse(url=authorize_url)


@router.get("/user/auth/callback")
async def linuxdo_callback(
    request: Request,
    code: str = "",
    state: str = "",
    db: AsyncSession = Depends(get_db),
):
    """处理 LinuxDo OAuth 回调。"""
    expected_state = request.session.get("linuxdo_oauth_state")
    request.session.pop("linuxdo_oauth_state", None)

    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="缺少授权 code")

    if not expected_state or state != expected_state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state 校验失败")

    try:
        from app.services.settings import settings_service

        oauth_config = await settings_service.get_linuxdo_oauth_config(db)
        base_url = str(request.base_url).rstrip("/")
        userinfo = await linuxdo_auth_service.exchange_code_for_userinfo(code, base_url, oauth_config)
        user = await linuxdo_auth_service.get_or_create_user(userinfo, db)

        request.session["user"] = {
            "id": user.id,
            "linuxdo_user_id": user.linuxdo_user_id,
            "username": user.username,
            "display_name": user.display_name,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "auth_provider": "linuxdo",
            "is_admin": False,
        }

        return RedirectResponse(url="/user/points")
    except Exception as exc:
        logger.error(f"LinuxDo OAuth 回调失败: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"LinuxDo 登录失败: {str(exc)}")


@router.post("/user/auth/logout")
async def linuxdo_logout(request: Request):
    """退出 LinuxDo 用户会话。"""
    request.session.pop("user", None)
    return {"success": True, "message": "已退出登录"}


@router.get("/user/points", response_class=HTMLResponse)
async def points_page(request: Request, db: AsyncSession = Depends(get_db)):
    """积分中心页面。"""
    from app.main import templates

    user_session = request.session.get("user")
    user_data = None
    recent_orders = []
    recent_points = []

    if user_session and user_session.get("auth_provider") == "linuxdo" and not user_session.get("is_admin"):
        result = await db.execute(select(LinuxDoUser).where(LinuxDoUser.id == user_session.get("id")))
        user = result.scalar_one_or_none()
        if user:
            user_data = {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "points": user.points,
                "last_sign_in_at": user.last_sign_in_at,
            }

            tx_result = await db.execute(
                select(PointTransaction)
                .where(PointTransaction.user_id == user.id)
                .order_by(desc(PointTransaction.created_at))
                .limit(10)
            )
            recent_points = tx_result.scalars().all()

            order_result = await db.execute(
                select(ShopOrder)
                .where(ShopOrder.user_id == user.id)
                .order_by(desc(ShopOrder.created_at))
                .limit(10)
            )
            recent_orders = order_result.scalars().all()

    return templates.TemplateResponse(
        "user/points.html",
        {
            "request": request,
            "user_data": user_data,
            "daily_points": int(settings.user_daily_signin_points),
            "redeem_cost": int(settings.shop_redeem_code_cost),
            "recent_orders": recent_orders,
            "recent_points": recent_points,
            "now": datetime.now(),
        },
    )


@router.get("/user/shop", response_class=HTMLResponse)
async def shop_page(request: Request, db: AsyncSession = Depends(get_db)):
    """积分商城页面。"""
    from app.main import templates

    user_session = request.session.get("user")
    user_data = None
    latest_order = None
    shop_items = await settings_service.get_shop_items(db)
    enabled_items = [i for i in shop_items if i.get("enabled")]
    announcement = await settings_service.get_announcement(db)

    if user_session and user_session.get("auth_provider") == "linuxdo" and not user_session.get("is_admin"):
        result = await db.execute(select(LinuxDoUser).where(LinuxDoUser.id == user_session.get("id")))
        user = result.scalar_one_or_none()
        if user:
            user_data = {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "points": user.points,
            }

            order_result = await db.execute(
                select(ShopOrder)
                .where(ShopOrder.user_id == user.id)
                .order_by(desc(ShopOrder.created_at))
                .limit(1)
            )
            latest_order = order_result.scalar_one_or_none()

    return templates.TemplateResponse(
        "user/shop.html",
        {
            "request": request,
            "user_data": user_data,
            "redeem_cost": int(settings.shop_redeem_code_cost),
            "latest_order": latest_order,
            "shop_items": enabled_items,
            "announcement": announcement,
        },
    )


@router.get("/user/api/me")
async def me(current_user: dict = Depends(require_linuxdo_user), db: AsyncSession = Depends(get_db)):
    """获取当前 LinuxDo 用户信息。"""
    result = await db.execute(select(LinuxDoUser).where(LinuxDoUser.id == current_user["id"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    return {
        "success": True,
        "user": {
            "id": user.id,
            "linuxdo_user_id": user.linuxdo_user_id,
            "username": user.username,
            "display_name": user.display_name,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "points": user.points,
            "last_sign_in_at": user.last_sign_in_at.isoformat() if user.last_sign_in_at else None,
        },
    }


@router.post("/user/api/sign-in")
async def daily_sign_in(
    current_user: dict = Depends(require_linuxdo_user),
    db: AsyncSession = Depends(get_db),
):
    """每日签到获取积分。"""
    result = await linuxdo_auth_service.daily_sign_in(current_user["id"], db)
    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error", "签到失败"))
    return result


@router.get("/user/api/shop/items")
async def shop_items(db: AsyncSession = Depends(get_db)):
    """积分商城商品列表（已上架）。"""
    items = await settings_service.get_shop_items(db)
    enabled_items = [
        {
            "key": i.get("key"),
            "name": i.get("name"),
            "desc": i.get("desc"),
            "points_cost": int(i.get("cost", 0) or 0),
        }
        for i in items if i.get("enabled")
    ]
    return {
        "success": True,
        "items": enabled_items,
    }

@router.post("/user/api/shop/buy")
async def shop_buy(
    body: dict = Body(default={}),
    current_user: dict = Depends(require_linuxdo_user),
    db: AsyncSession = Depends(get_db),
):
    """购买商城商品。"""
    item_key = (body or {}).get("item_key") or "redeem_code"

    items = await settings_service.get_shop_items(db)
    target = next((i for i in items if i.get("key") == item_key and i.get("enabled")), None)
    if not target:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="商品不存在或已下架")

    cost = int(target.get("cost", 0) or 0)
    if cost <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="商品价格异常")

    result = await linuxdo_auth_service.buy_shop_item(
        user_id=current_user["id"],
        item_key=item_key,
        cost=cost,
        db=db,
    )

    if not result["success"]:
        detail = result.get("error", "购买失败")
        status_code = status.HTTP_400_BAD_REQUEST
        if "库存" in detail:
            status_code = status.HTTP_409_CONFLICT
        raise HTTPException(status_code=status_code, detail=detail)
    return result
