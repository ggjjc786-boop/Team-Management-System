"""
用户路由
处理用户页面渲染
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import ExclusiveInvite, Team, LinuxDoUser

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(
    tags=["user"]
)


@router.get("/", response_class=HTMLResponse)
async def redeem_page(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    用户兑换页面

    Args:
        request: FastAPI Request 对象
        db: 数据库会话

    Returns:
        用户兑换页面 HTML
    """
    try:
        from app.main import templates
        from app.services.team import TeamService
        from app.services.settings import settings_service
        
        team_service = TeamService()
        remaining_spots = await team_service.get_total_available_spots(db)
        warranty_days = await settings_service.get_warranty_days(db)

        user_data = None
        user_session = request.session.get("user")
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
                }

        # 获取公告
        announcement_data = await settings_service.get_announcement(db)
        announcement = announcement_data["content"] if announcement_data["enabled"] and announcement_data["content"] else None
        
        # 获取节日装饰
        festive_config = await settings_service.get_festive_config(db)

        logger.info(f"用户访问兑换页面，剩余车位: {remaining_spots}")

        return templates.TemplateResponse(
            "user/redeem.html",
            {
                "request": request,
                "remaining_spots": remaining_spots,
                "warranty_days": warranty_days,
                "announcement": announcement,
                "user_data": user_data,
                "festive_enabled": festive_config["enabled"]
            }
        )

    except Exception as e:
        logger.error(f"渲染兑换页面失败: {e}")
        return HTMLResponse(
            content=f"<h1>页面加载失败</h1><p>{str(e)}</p>",
            status_code=500
        )


@router.get("/user/freespot", response_class=HTMLResponse)
@router.get("/free-spot", response_class=HTMLResponse)
async def free_spot_page(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """免费车位页面"""
    try:
        from app.main import templates
        from app.services.settings import settings_service
        festive_config = await settings_service.get_festive_config(db)
        return templates.TemplateResponse("user/freespot.html", {
            "request": request,
            "festive_enabled": festive_config["enabled"]
        })
    except Exception as e:
        logger.error(f"渲染免费车位页面失败: {e}")
        return HTMLResponse(
            content=f"<h1>页面加载失败</h1><p>{str(e)}</p>",
            status_code=500
        )


@router.get("/user/waitingroom", response_class=HTMLResponse)
@router.get("/user/waiting-room", response_class=HTMLResponse)
@router.get("/waiting-room", response_class=HTMLResponse)
async def waiting_room_page(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """候车室页面"""
    try:
        from app.main import templates
        from app.services.settings import settings_service

        idc_config = await settings_service.get_idc_config(db)
        festive_config = await settings_service.get_festive_config(db)

        return templates.TemplateResponse(
            "user/waitingroom.html",
            {
                "request": request,
                "idc_enabled": idc_config.get("enabled", False),
                "idc_amount": idc_config.get("amount", "6.66"),
                "festive_enabled": festive_config["enabled"],
            }
        )
    except Exception as e:
        logger.error(f"渲染候车室页面失败: {e}")
        return HTMLResponse(
            content=f"<h1>页面加载失败</h1><p>{str(e)}</p>",
            status_code=500
        )


@router.get("/user/exclusive_join", response_class=HTMLResponse)
@router.get("/user/exclusive-join", response_class=HTMLResponse)
async def exclusive_join_page(
    request: Request,
    token: str = Query(default=""),
    db: AsyncSession = Depends(get_db)
):
    """打赏用户专属上车页面"""
    from app.main import templates

    error_msg = None
    invite_data = None

    try:
        if not token:
            error_msg = "缺少邀请令牌"
            return templates.TemplateResponse(
                "user/exclusive_join.html",
                {"request": request, "error_msg": error_msg, "invite_data": invite_data}
            )

        invite_result = await db.execute(
            select(ExclusiveInvite).where(ExclusiveInvite.token == token)
        )
        invite = invite_result.scalar_one_or_none()

        if not invite:
            error_msg = "邀请链接不存在或已失效"
        elif invite.used:
            error_msg = "该专属链接已被使用"
        elif invite.expires_at and invite.expires_at < datetime.utcnow():
            error_msg = "该专属链接已过期"
        else:
            team_result = await db.execute(
                select(Team).where(Team.id == invite.team_id)
            )
            team = team_result.scalar_one_or_none()

            if not team:
                error_msg = "目标 Team 不存在"
            elif team.status in ("expired", "error"):
                error_msg = "当前 Team 不可用"
            elif team.current_members >= team.max_members:
                error_msg = "当前 Team 车位已满"
            else:
                invite_data = {
                    "email": invite.email,
                    "team_name": team.team_name or f"Team {team.id}",
                    "current_members": team.current_members,
                    "max_members": team.max_members,
                }

        return templates.TemplateResponse(
            "user/exclusive_join.html",
            {"request": request, "error_msg": error_msg, "invite_data": invite_data}
        )

    except Exception as e:
        logger.error(f"渲染专属上车页面失败: {e}")
        return templates.TemplateResponse(
            "user/exclusive_join.html",
            {"request": request, "error_msg": "页面加载失败，请稍后重试", "invite_data": None}
        )
