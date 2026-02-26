"""
管理员路由
处理管理员面板的所有页面和操作
"""
import logging
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.database import get_db
from app.dependencies.auth import require_admin
from app.models import WaitingRoom, ExclusiveInvite
from app.services.team import TeamService
from app.services.redemption import RedemptionService
from app.services.waiting_room import waiting_room_service

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

# 服务实例
team_service = TeamService()
redemption_service = RedemptionService()


# 请求模型
class TeamImportRequest(BaseModel):
    """Team 导入请求"""
    import_type: str = Field(..., description="导入类型: single 或 batch")
    access_token: Optional[str] = Field(None, description="AT Token (单个导入)")
    email: Optional[str] = Field(None, description="邮箱 (单个导入)")
    account_id: Optional[str] = Field(None, description="Account ID (单个导入)")
    content: Optional[str] = Field(None, description="批量导入内容")


class AddMemberRequest(BaseModel):
    """添加成员请求"""
    email: str = Field(..., description="成员邮箱")


class ToggleFreeSpotRequest(BaseModel):
    """切换免费车位请求"""
    is_free_spot: bool = Field(..., description="是否设为免费车位")


class ToggleExclusiveRequest(BaseModel):
    """切换打赏专属请求"""
    is_exclusive: bool = Field(..., description="是否设为打赏用户专属")


class CodeGenerateRequest(BaseModel):
    """兑换码生成请求"""
    type: str = Field(..., description="生成类型: single 或 batch")
    code: Optional[str] = Field(None, description="自定义兑换码 (单个生成)")
    count: Optional[int] = Field(None, description="生成数量 (批量生成)")
    expires_days: Optional[int] = Field(None, description="有效期天数")
    is_warranty: bool = Field(False, description="是否为质保兑换码")
    warranty_days: Optional[int] = Field(None, description="质保天数（质保码时可设置，空则用全局默认）")
    is_points_only: bool = Field(False, description="是否为积分兑换专属")


class ExclusiveInviteBatchRequest(BaseModel):
    """批量发送打赏专属邀请请求"""
    team_id: int = Field(..., description="专属 Team ID")
    emails: list[str] = Field(..., description="邮箱列表")


class ExclusiveInvitePriorityRequest(BaseModel):
    """向优先用户发送打赏专属邀请请求"""
    team_id: int = Field(..., description="专属 Team ID")


def _make_site_url(request: Request) -> str:
    forwarded_proto = request.headers.get("x-forwarded-proto")
    forwarded_host = request.headers.get("x-forwarded-host")
    if forwarded_proto and forwarded_host:
        return f"{forwarded_proto}://{forwarded_host}"
    return f"{request.url.scheme}://{request.url.netloc}"


def _build_exclusive_email_html(invite_url: str, to_email: str, team_name: str) -> str:
    return (
        "<!DOCTYPE html>"
        "<html lang=\"zh-CN\"><head><meta charset=\"UTF-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\">"
        "</head><body style=\"margin:0;padding:0;background:#f5f5f5;\">"
        "<table width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" style=\"background:#f5f5f5;padding:40px 0;\">"
        "<tr><td align=\"center\">"
        "<table width=\"560\" cellpadding=\"0\" cellspacing=\"0\" style=\"background:#ffffff;border-radius:8px;"
        "border:1px solid #e5e5e5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;\">"
        "<tr><td style=\"padding:32px 40px 24px;border-bottom:1px solid #f0f0f0;\">"
        "<h1 style=\"margin:0;font-size:20px;color:#333;font-weight:600;\">GPT Team - 打赏专属邀请</h1>"
        "</td></tr>"
        "<tr><td style=\"padding:32px 40px;\">"
        f"<p style=\"margin:0 0 16px;font-size:15px;line-height:1.7;color:#333;\">{to_email} 您好，</p>"
        f"<p style=\"margin:0 0 16px;font-size:15px;line-height:1.7;color:#333;\">您收到了 <strong>{team_name}</strong> 的打赏专属上车链接。</p>"
        "<p style=\"margin:0 0 24px;font-size:15px;line-height:1.7;color:#333;\">该链接有效期为 5 小时，请尽快完成上车。</p>"
        "<table cellpadding=\"0\" cellspacing=\"0\" style=\"margin:0 0 24px;\">"
        "<tr><td align=\"center\" style=\"background:#7c3aed;border-radius:6px;\">"
        f"<a href=\"{invite_url}\" target=\"_blank\" style=\"display:inline-block;padding:12px 32px;"
        "font-size:15px;font-weight:600;color:#ffffff;text-decoration:none;\">"
        "立即专属上车</a>"
        "</td></tr></table>"
        f"<p style=\"margin:0;font-size:12px;color:#999;line-height:1.6;word-break:break-all;\">备用链接：{invite_url}</p>"
        "</td></tr>"
        "<tr><td style=\"padding:20px 40px;border-top:1px solid #f0f0f0;\">"
        "<p style=\"margin:0;font-size:12px;color:#aaa;line-height:1.5;\">此邮件由系统自动发送，请勿直接回复。</p>"
        "</td></tr>"
        "</table></td></tr></table></body></html>"
    )


async def _send_exclusive_invite_email(
    to_email: str,
    invite_url: str,
    team_name: str,
    db: AsyncSession
) -> bool:
    from app.services.settings import settings_service

    email_config = await settings_service.get_email_config(db)

    smtp_enabled = bool(email_config.get("smtp_enabled"))
    smtp_host = str(email_config.get("smtp_host") or "").strip()
    smtp_port = int(email_config.get("smtp_port") or 465)
    smtp_username = str(email_config.get("smtp_username") or "").strip()
    smtp_password = str(email_config.get("smtp_password") or "").strip()
    smtp_from_email = str(email_config.get("smtp_from_email") or "").strip()
    smtp_use_ssl = bool(email_config.get("smtp_use_ssl", True))

    resend_enabled = bool(email_config.get("resend_enabled"))
    resend_api_key = str(email_config.get("resend_api_key") or "").strip()
    resend_from_email = str(email_config.get("resend_from_email") or "").strip()

    # 向后兼容：数据库未配置时回退环境变量
    if not smtp_host:
        smtp_host = os.getenv("SMTP_HOST", "").strip()
    if not smtp_username:
        smtp_username = os.getenv("SMTP_USERNAME", "").strip()
    if not smtp_password:
        smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
    if not smtp_from_email:
        smtp_from_email = os.getenv("SMTP_FROM_EMAIL", "").strip()
    if not resend_api_key:
        resend_api_key = os.getenv("RESEND_API_KEY", "").strip()
    if not resend_from_email:
        resend_from_email = os.getenv("RESEND_FROM_EMAIL", "").strip()

    if not smtp_enabled and smtp_host and smtp_username and smtp_password:
        smtp_enabled = True
    if not resend_enabled and resend_api_key and resend_from_email:
        resend_enabled = True

    html_content = _build_exclusive_email_html(invite_url, to_email, team_name)

    if smtp_enabled and smtp_host and smtp_username and smtp_password:
        smtp_config = {
            "enabled": True,
            "host": smtp_host,
            "port": smtp_port,
            "username": smtp_username,
            "password": smtp_password,
            "from_email": smtp_from_email or smtp_username,
            "use_ssl": smtp_use_ssl,
        }
        return await waiting_room_service._send_via_smtp(smtp_config, to_email, html_content)

    if resend_enabled and resend_api_key and resend_from_email:
        return await waiting_room_service._send_via_resend(
            api_key=resend_api_key,
            from_email=resend_from_email,
            to_email=to_email,
            html_content=html_content,
        )

    return False


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    管理员面板首页

    Args:
        request: FastAPI Request 对象
        db: 数据库会话
        current_user: 当前用户（需要登录）

    Returns:
        管理员面板首页 HTML
    """
    try:
        # 导入模板引擎
        from app.main import templates

        logger.info("管理员访问控制台")

        # 获取所有 Team 列表
        teams_result = await team_service.get_all_teams(db)
        teams = teams_result.get("teams", [])

        # 获取兑换码统计
        codes_result = await redemption_service.get_all_codes(db)
        all_codes = codes_result.get("codes", [])

        # 计算统计数据
        stats = {
            "total_teams": len(teams),
            "available_teams": len([t for t in teams if t["status"] == "active" and t["current_members"] < t["max_members"]]),
            "total_codes": len(all_codes),
            "used_codes": len([c for c in all_codes if c["status"] == "used"])
        }

        return templates.TemplateResponse(
            "admin/index.html",
            {
                "request": request,
                "user": current_user,
                "active_page": "dashboard",
                "teams": teams,
                "stats": stats
            }
        )

    except Exception as e:
        logger.error(f"加载管理员面板失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"加载管理员面板失败: {str(e)}"
        )


@router.post("/teams/{team_id}/delete")
async def delete_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    删除 Team

    Args:
        team_id: Team ID
        db: 数据库会话
        current_user: 当前用户（需要登录）

    Returns:
        删除结果
    """
    try:
        logger.info(f"管理员删除 Team: {team_id}")

        result = await team_service.delete_team(team_id, db)

        if not result["success"]:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=result
            )

        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"删除 Team 失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": f"删除 Team 失败: {str(e)}"
            }
        )


@router.post("/teams/{team_id}/toggle-free-spot")
async def toggle_team_free_spot(
    team_id: int,
    toggle_data: ToggleFreeSpotRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """切换 Team 免费车位状态"""
    try:
        logger.info(f"管理员切换 Team {team_id} 免费车位状态: {toggle_data.is_free_spot}")

        result = await team_service.toggle_free_spot(
            team_id=team_id,
            is_free_spot=toggle_data.is_free_spot,
            db_session=db
        )

        if not result["success"]:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=result
            )

        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"切换免费车位状态失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": f"操作失败: {str(e)}"
            }
        )


@router.post("/teams/{team_id}/toggle-exclusive")
async def toggle_team_exclusive(
    team_id: int,
    toggle_data: ToggleExclusiveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """切换 Team 打赏用户专属状态"""
    try:
        logger.info(f"管理员切换 Team {team_id} 打赏专属状态: {toggle_data.is_exclusive}")

        result = await team_service.toggle_exclusive(
            team_id=team_id,
            is_exclusive=toggle_data.is_exclusive,
            db_session=db
        )

        if not result["success"]:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=result
            )

        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"切换打赏专属状态失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": f"操作失败: {str(e)}"
            }
        )




@router.post("/teams/import")
async def team_import(
    import_data: TeamImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    处理 Team 导入

    Args:
        import_data: 导入数据
        db: 数据库会话
        current_user: 当前用户（需要登录）

    Returns:
        导入结果
    """
    try:
        logger.info(f"管理员导入 Team: {import_data.import_type}")

        if import_data.import_type == "single":
            # 单个导入
            if not import_data.access_token:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "success": False,
                        "error": "Access Token 不能为空"
                    }
                )

            result = await team_service.import_team_single(
                access_token=import_data.access_token,
                db_session=db,
                email=import_data.email,
                account_id=import_data.account_id
            )

            if not result["success"]:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=result
                )

            return JSONResponse(content=result)

        elif import_data.import_type == "batch":
            # 批量导入
            if not import_data.content:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "success": False,
                        "error": "批量导入内容不能为空"
                    }
                )

            result = await team_service.import_team_batch(
                text=import_data.content,
                db_session=db
            )

            return JSONResponse(content=result)

        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "error": "无效的导入类型"
                }
            )

    except Exception as e:
        logger.error(f"导入 Team 失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": f"导入失败: {str(e)}"
            }
        )





@router.get("/teams/{team_id}/members/list")
async def team_members_list(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    获取 Team 成员列表 (JSON)

    Args:
        team_id: Team ID
        db: 数据库会话
        current_user: 当前用户（需要登录）

    Returns:
        成员列表 JSON
    """
    try:
        # 获取成员列表
        result = await team_service.get_team_members(team_id, db)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"获取成员列表失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": f"获取成员列表失败: {str(e)}"
            }
        )


@router.post("/teams/{team_id}/members/add")
async def add_team_member(
    team_id: int,
    member_data: AddMemberRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    添加 Team 成员

    Args:
        team_id: Team ID
        member_data: 成员数据
        db: 数据库会话
        current_user: 当前用户（需要登录）

    Returns:
        添加结果
    """
    try:
        logger.info(f"管理员添加成员到 Team {team_id}: {member_data.email}")

        result = await team_service.add_team_member(
            team_id=team_id,
            email=member_data.email,
            db_session=db
        )

        if not result["success"]:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=result
            )

        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"添加成员失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": f"添加成员失败: {str(e)}"
            }
        )


@router.post("/teams/{team_id}/members/{user_id}/delete")
async def delete_team_member(
    team_id: int,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    删除 Team 成员

    Args:
        team_id: Team ID
        user_id: 用户 ID
        db: 数据库会话
        current_user: 当前用户（需要登录）

    Returns:
        删除结果
    """
    try:
        logger.info(f"管理员从 Team {team_id} 删除成员: {user_id}")

        result = await team_service.delete_team_member(
            team_id=team_id,
            user_id=user_id,
            db_session=db
        )

        if not result["success"]:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=result
            )

        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"删除成员失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": f"删除成员失败: {str(e)}"
            }
        )


@router.post("/teams/{team_id}/invites/revoke")
async def revoke_team_invite(
    team_id: int,
    member_data: AddMemberRequest, # 使用相同的包含 email 的模型
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    撤回 Team 邀请

    Args:
        team_id: Team ID
        member_data: 成员数据 (包含 email)
        db: 数据库会话
        current_user: 当前用户（需要登录）

    Returns:
        撤回结果
    """
    try:
        logger.info(f"管理员从 Team {team_id} 撤回邀请: {member_data.email}")

        result = await team_service.revoke_team_invite(
            team_id=team_id,
            email=member_data.email,
            db_session=db
        )

        if not result["success"]:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=result
            )

        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"撤回邀请失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": f"撤回邀请失败: {str(e)}"
            }
        )


# ==================== 兑换码管理路由 ====================

@router.get("/codes", response_class=HTMLResponse)
async def codes_list_page(
    request: Request,
    filter_status: Optional[str] = "all",
    page: Optional[str] = "1",
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    兑换码列表页面

    Args:
        request: FastAPI Request 对象
        db: 数据库会话
        current_user: 当前用户（需要登录）

    Returns:
        兑换码列表页面 HTML
    """
    try:
        from app.main import templates
        import math

        # 解析参数
        valid_status = {"all", "unused", "used", "expired"}
        current_status = (filter_status or "all").strip().lower()
        if current_status not in valid_status:
            current_status = "all"

        try:
            current_page = int(page) if page and str(page).strip() else 1
        except (ValueError, TypeError):
            current_page = 1

        logger.info("管理员访问兑换码列表页面")

        # 获取所有兑换码
        codes_result = await redemption_service.get_all_codes(db)
        all_codes = codes_result.get("codes", [])

        # 计算统计数据
        stats = {
            "total": len(all_codes),
            "unused": len([c for c in all_codes if c["status"] == "unused"]),
            "used": len([c for c in all_codes if c["status"] == "used"]),
            "expired": len([c for c in all_codes if c["status"] == "expired"])
        }

        # 格式化日期时间
        from datetime import datetime
        for code in all_codes:
            if code.get("created_at"):
                dt = datetime.fromisoformat(code["created_at"])
                code["created_at"] = dt.strftime("%Y-%m-%d %H:%M")
            if code.get("expires_at"):
                dt = datetime.fromisoformat(code["expires_at"])
                code["expires_at"] = dt.strftime("%Y-%m-%d %H:%M")
            if code.get("used_at"):
                dt = datetime.fromisoformat(code["used_at"])
                code["used_at"] = dt.strftime("%Y-%m-%d %H:%M")

        # 按状态筛选
        filtered_codes = all_codes
        if current_status != "all":
            filtered_codes = [c for c in all_codes if c.get("status") == current_status]

        # 分页
        per_page = 20
        total_filtered = len(filtered_codes)
        total_pages = math.ceil(total_filtered / per_page) if total_filtered > 0 else 1

        if current_page < 1:
            current_page = 1
        if current_page > total_pages:
            current_page = total_pages

        start_idx = (current_page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_codes = filtered_codes[start_idx:end_idx]

        return templates.TemplateResponse(
            "admin/codes/index.html",
            {
                "request": request,
                "user": current_user,
                "active_page": "codes",
                "codes": paginated_codes,
                "stats": stats,
                "current_status": current_status,
                "current_page": current_page,
                "total_pages": total_pages,
                "total_filtered": total_filtered
            }
        )

    except Exception as e:
        logger.error(f"加载兑换码列表页面失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"加载页面失败: {str(e)}"
        )




@router.post("/codes/generate")
async def generate_codes(
    generate_data: CodeGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    处理兑换码生成

    Args:
        generate_data: 生成数据
        db: 数据库会话
        current_user: 当前用户（需要登录）

    Returns:
        生成结果
    """
    try:
        logger.info(f"管理员生成兑换码: {generate_data.type}")

        if generate_data.type == "single":
            # 单个生成
            result = await redemption_service.generate_code_single(
                db_session=db,
                code=generate_data.code,
                expires_days=generate_data.expires_days,
                is_warranty=generate_data.is_warranty,
                warranty_days=generate_data.warranty_days if generate_data.is_warranty else None,
                is_points_only=generate_data.is_points_only
            )

            if not result["success"]:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=result
                )

            return JSONResponse(content=result)

        elif generate_data.type == "batch":
            # 批量生成
            if not generate_data.count:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "success": False,
                        "error": "生成数量不能为空"
                    }
                )

            result = await redemption_service.generate_code_batch(
                db_session=db,
                count=generate_data.count,
                expires_days=generate_data.expires_days,
                is_warranty=generate_data.is_warranty,
                warranty_days=generate_data.warranty_days if generate_data.is_warranty else None,
                is_points_only=generate_data.is_points_only
            )

            if not result["success"]:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=result
                )

            return JSONResponse(content=result)

        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "error": "无效的生成类型"
                }
            )

    except Exception as e:
        logger.error(f"生成兑换码失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": f"生成失败: {str(e)}"
            }
        )


@router.post("/codes/generate-test")
async def generate_test_code(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    生成测试兑换码（仅用于前端动画测试，不做真实邀请）。
    """
    try:
        logger.info("管理员生成测试兑换码")

        result = await redemption_service.generate_test_code(db_session=db)

        if not result["success"]:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=result
            )

        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"生成测试兑换码失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": f"生成测试兑换码失败: {str(e)}"
            }
        )


@router.post("/codes/{code}/delete")
async def delete_code(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    删除兑换码

    Args:
        code: 兑换码
        db: 数据库会话
        current_user: 当前用户（需要登录）

    Returns:
        删除结果
    """
    try:
        logger.info(f"管理员删除兑换码: {code}")

        result = await redemption_service.delete_code(code, db)

        if not result["success"]:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=result
            )

        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"删除兑换码失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": f"删除失败: {str(e)}"
            }
        )


@router.get("/codes/export")
async def export_codes(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    导出兑换码为Excel文件

    Args:
        db: 数据库会话
        current_user: 当前用户（需要登录）

    Returns:
        兑换码Excel文件
    """
    try:
        from fastapi.responses import Response
        from datetime import datetime
        import xlsxwriter
        from io import BytesIO

        logger.info("管理员导出兑换码为Excel")

        # 获取所有兑换码
        codes_result = await redemption_service.get_all_codes(db)
        all_codes = codes_result.get("codes", [])

        # 创建Excel文件到内存
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('兑换码列表')

        # 定义格式
        header_format = workbook.add_format({
            'bold': True,
            'fg_color': '#4F46E5',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        cell_format = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'border': 1
        })

        # 设置列宽
        worksheet.set_column('A:A', 25)  # 兑换码
        worksheet.set_column('B:B', 12)  # 状态
        worksheet.set_column('C:C', 18)  # 创建时间
        worksheet.set_column('D:D', 18)  # 过期时间
        worksheet.set_column('E:E', 30)  # 使用者邮箱
        worksheet.set_column('F:F', 18)  # 使用时间

        # 写入表头
        headers = ['兑换码', '状态', '创建时间', '过期时间', '使用者邮箱', '使用时间']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # 写入数据
        for row, code in enumerate(all_codes, start=1):
            status_text = {
                'unused': '未使用',
                'used': '已使用',
                'expired': '已过期'
            }.get(code['status'], code['status'])

            worksheet.write(row, 0, code['code'], cell_format)
            worksheet.write(row, 1, status_text, cell_format)
            worksheet.write(row, 2, code.get('created_at', '-'), cell_format)
            worksheet.write(row, 3, code.get('expires_at', '永久有效'), cell_format)
            worksheet.write(row, 4, code.get('used_by_email', '-'), cell_format)
            worksheet.write(row, 5, code.get('used_at', '-'), cell_format)

        # 关闭workbook
        workbook.close()

        # 获取Excel数据
        excel_data = output.getvalue()
        output.close()

        # 生成文件名
        filename = f"redemption_codes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        # 返回Excel文件
        return Response(
            content=excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        logger.error(f"导出兑换码失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}"
        )


@router.get("/records", response_class=HTMLResponse)
async def records_page(
    request: Request,
    email: Optional[str] = None,
    code: Optional[str] = None,
    team_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: Optional[str] = "1",
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    使用记录页面

    Args:
        request: FastAPI Request 对象
        email: 邮箱筛选
        code: 兑换码筛选
        team_id: Team ID 筛选
        start_date: 开始日期
        end_date: 结束日期
        page: 页码
        db: 数据库会话
        current_user: 当前用户（需要登录）

    Returns:
        使用记录页面 HTML
    """
    try:
        from app.main import templates
        from datetime import datetime, timedelta
        import math

        # 解析参数
        try:
            actual_team_id = int(team_id) if team_id and team_id.strip() else None
        except (ValueError, TypeError):
            actual_team_id = None
            
        try:
            page_int = int(page) if page and page.strip() else 1
        except (ValueError, TypeError):
            page_int = 1
            
        logger.info(f"管理员访问使用记录页面 (page={page_int})")

        # 获取所有记录
        records_result = await redemption_service.get_all_records(db)
        all_records = records_result.get("records", [])

        # 筛选记录
        filtered_records = []
        for record in all_records:
            # 邮箱筛选
            if email and email.lower() not in record["email"].lower():
                continue

            # 兑换码筛选
            if code and code.lower() not in record["code"].lower():
                continue

            # Team ID 筛选
            if actual_team_id is not None and record["team_id"] != actual_team_id:
                continue

            # 日期范围筛选
            if start_date or end_date:
                try:
                    record_date = datetime.fromisoformat(record["redeemed_at"]).date()

                    if start_date:
                        start = datetime.strptime(start_date, "%Y-%m-%d").date()
                        if record_date < start:
                            continue

                    if end_date:
                        end = datetime.strptime(end_date, "%Y-%m-%d").date()
                        if record_date > end:
                            continue
                except:
                    pass

            filtered_records.append(record)

        # 获取Team信息并关联到记录
        teams_result = await team_service.get_all_teams(db)
        teams = teams_result.get("teams", [])
        team_map = {team["id"]: team for team in teams}

        # 为记录添加Team名称
        for record in filtered_records:
            team = team_map.get(record["team_id"])
            record["team_name"] = team["team_name"] if team else None

        # 计算统计数据
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)

        stats = {
            "total": len(filtered_records),
            "today": 0,
            "this_week": 0,
            "this_month": 0
        }

        for record in filtered_records:
            try:
                record_time = datetime.fromisoformat(record["redeemed_at"])
                if record_time >= today_start:
                    stats["today"] += 1
                if record_time >= week_start:
                    stats["this_week"] += 1
                if record_time >= month_start:
                    stats["this_month"] += 1
            except:
                pass

        # 分页
        per_page = 20
        total_records = len(filtered_records)
        total_pages = math.ceil(total_records / per_page) if total_records > 0 else 1

        # 确保页码有效
        if page_int < 1:
            page_int = 1
        if page_int > total_pages:
            page_int = total_pages

        start_idx = (page_int - 1) * per_page
        end_idx = start_idx + per_page
        paginated_records = filtered_records[start_idx:end_idx]

        # 格式化时间
        for record in paginated_records:
            try:
                dt = datetime.fromisoformat(record["redeemed_at"])
                record["redeemed_at"] = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass

        return templates.TemplateResponse(
            "admin/records/index.html",
            {
                "request": request,
                "user": current_user,
                "active_page": "records",
                "records": paginated_records,
                "stats": stats,
                "filters": {
                    "email": email,
                    "code": code,
                    "team_id": team_id,
                    "start_date": start_date,
                    "end_date": end_date
                },
                "pagination": {
                    "current_page": page_int,
                    "total_pages": total_pages,
                    "total": total_records,
                    "per_page": per_page
                }
            }
        )

    except Exception as e:
        logger.error(f"获取使用记录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取使用记录失败: {str(e)}"
        )


# ==================== LinuxDo 用户管理路由 ====================


class AdjustPointsRequest(BaseModel):
    """积分调整请求"""
    change: int = Field(..., description="积分变动，正数增加负数扣减")
    description: str = Field("管理员手动调整", description="变动说明")


@router.get("/users", response_class=HTMLResponse)
async def admin_users_page(
    request: Request,
    search: Optional[str] = None,
    page: Optional[str] = "1",
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """LinuxDo 用户管理页面"""
    from app.main import templates
    from app.models import LinuxDoUser

    try:
        page_num = max(1, int(page or "1"))
    except ValueError:
        page_num = 1
    page_size = 20

    query = select(LinuxDoUser)
    count_query = select(func.count(LinuxDoUser.id))

    if search:
        search_filter = or_(
            LinuxDoUser.username.contains(search),
            LinuxDoUser.display_name.contains(search),
            LinuxDoUser.email.contains(search),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    total_pages = max(1, (total + page_size - 1) // page_size)
    page_num = min(page_num, total_pages)

    query = query.order_by(LinuxDoUser.created_at.desc()).offset((page_num - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()

    return templates.TemplateResponse(
        "admin/users/index.html",
        {
            "request": request,
            "user": current_user,
            "active_page": "users",
            "users": users,
            "search": search or "",
            "current_page": page_num,
            "total_pages": total_pages,
            "total_users": total,
        }
    )


@router.post("/users/{user_id}/adjust-points")
async def admin_adjust_points(
    user_id: int,
    payload: AdjustPointsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """管理员手动调整用户积分"""
    from app.models import LinuxDoUser, PointTransaction

    result = await db.execute(select(LinuxDoUser).where(LinuxDoUser.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    if payload.change == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="变动值不能为 0")

    new_points = user.points + payload.change
    if new_points < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"积分不足，当前 {user.points}，调整 {payload.change}")

    user.points = new_points
    db.add(PointTransaction(
        user_id=user.id,
        change=payload.change,
        type="adjust",
        description=payload.description or "管理员手动调整",
    ))
    await db.commit()
    await db.refresh(user)

    return {
        "success": True,
        "message": f"已调整 {payload.change:+d} 积分",
        "points": user.points,
    }


# ==================== 候车室管理路由 ====================

@router.get("/waiting-room", response_class=HTMLResponse)
async def waiting_room_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """候车室管理页面"""
    try:
        from app.main import templates

        logger.info("管理员访问候车室管理页面")

        waiting_list = await waiting_room_service.get_waiting_list(db)

        total_count = len(waiting_list)
        waiting_count = len([item for item in waiting_list if not item.get("notified")])
        notified_count = len([item for item in waiting_list if item.get("notified")])
        priority_count = len([item for item in waiting_list if item.get("is_priority") and not item.get("notified")])

        teams_result = await team_service.get_all_teams(db)
        all_teams = teams_result.get("teams", [])
        exclusive_teams = [
            team for team in all_teams
            if team.get("is_exclusive") and team.get("status") == "active" and team.get("current_members", 0) < team.get("max_members", 0)
        ]

        return templates.TemplateResponse(
            "admin/waitingroom/index.html",
            {
                "request": request,
                "user": current_user,
                "active_page": "waiting_room",
                "waiting_list": waiting_list,
                "total_count": total_count,
                "waiting_count": waiting_count,
                "priority_count": priority_count,
                "notified_count": notified_count,
                "exclusive_teams": exclusive_teams,
                "idc_orders": []
            }
        )

    except Exception as e:
        logger.error(f"加载候车室页面失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"加载候车室页面失败: {str(e)}"
        )


@router.post("/waiting-room/notify-all")
async def notify_all_waiting_users(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """通知所有未通知的候车用户"""
    try:
        from app.services.settings import settings_service

        email_config = await settings_service.get_email_config(db)
        smtp_config = {
            "enabled": bool(email_config.get("smtp_enabled")),
            "host": str(email_config.get("smtp_host") or "").strip(),
            "port": int(email_config.get("smtp_port") or 465),
            "username": str(email_config.get("smtp_username") or "").strip(),
            "password": str(email_config.get("smtp_password") or "").strip(),
            "from_email": str(email_config.get("smtp_from_email") or "").strip(),
            "use_ssl": bool(email_config.get("smtp_use_ssl", True)),
        }
        resend_api_key = str(email_config.get("resend_api_key") or "").strip() if email_config.get("resend_enabled") else ""
        resend_from_email = str(email_config.get("resend_from_email") or "").strip() if email_config.get("resend_enabled") else ""

        result = await waiting_room_service.notify_all(
            db,
            resend_api_key=resend_api_key,
            from_email=resend_from_email,
            smtp_config=smtp_config,
        )
        status_code = status.HTTP_200_OK if result.get("success") else status.HTTP_400_BAD_REQUEST
        return JSONResponse(status_code=status_code, content=result)
    except Exception as e:
        logger.error(f"通知所有候车用户失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"通知失败: {str(e)}"}
        )


@router.post("/waiting-room/notify-priority")
async def notify_priority_waiting_users(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """仅通知优先候车用户"""
    try:
        from app.services.settings import settings_service

        email_config = await settings_service.get_email_config(db)
        smtp_config = {
            "enabled": bool(email_config.get("smtp_enabled")),
            "host": str(email_config.get("smtp_host") or "").strip(),
            "port": int(email_config.get("smtp_port") or 465),
            "username": str(email_config.get("smtp_username") or "").strip(),
            "password": str(email_config.get("smtp_password") or "").strip(),
            "from_email": str(email_config.get("smtp_from_email") or "").strip(),
            "use_ssl": bool(email_config.get("smtp_use_ssl", True)),
        }
        resend_api_key = str(email_config.get("resend_api_key") or "").strip() if email_config.get("resend_enabled") else ""
        resend_from_email = str(email_config.get("resend_from_email") or "").strip() if email_config.get("resend_enabled") else ""

        result = await waiting_room_service.notify_priority(
            db,
            resend_api_key=resend_api_key,
            from_email=resend_from_email,
            smtp_config=smtp_config,
        )
        status_code = status.HTTP_200_OK if result.get("success") else status.HTTP_400_BAD_REQUEST
        return JSONResponse(status_code=status_code, content=result)
    except Exception as e:
        logger.error(f"通知优先候车用户失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"通知失败: {str(e)}"}
        )


@router.post("/waiting-room/clear")
async def clear_notified_waiting_entries(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """清除已通知的候车记录"""
    try:
        success = await waiting_room_service.clear_notified(db)
        if success:
            return JSONResponse(content={"success": True, "message": "已清除已通知记录"})
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "error": "清除失败"}
        )
    except Exception as e:
        logger.error(f"清除已通知候车记录失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"清除失败: {str(e)}"}
        )


@router.post("/waiting-room/delete/{entry_id}")
async def delete_waiting_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """删除单个候车记录"""
    try:
        success = await waiting_room_service.delete_entry(db, entry_id)
        if success:
            return JSONResponse(content={"success": True, "message": "已删除"})
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"success": False, "error": "记录不存在"}
        )
    except Exception as e:
        logger.error(f"删除候车记录失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"删除失败: {str(e)}"}
        )


@router.post("/exclusive-invite/send-batch")
async def send_exclusive_invite_batch(
    request: Request,
    payload: ExclusiveInviteBatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """批量发送打赏专属上车链接"""
    try:
        emails = []
        seen = set()
        for raw_email in payload.emails:
            email = (raw_email or "").strip().lower()
            if email and email not in seen:
                seen.add(email)
                emails.append(email)

        if not emails:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "error": "邮箱列表不能为空"}
            )

        teams_result = await team_service.get_all_teams(db)
        all_teams = teams_result.get("teams", [])
        selected_team = next((t for t in all_teams if t.get("id") == payload.team_id), None)
        if not selected_team:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "error": "Team 不存在"}
            )

        team_name = selected_team.get("team_name") or f"Team #{payload.team_id}"
        base_url = _make_site_url(request)

        results = []
        for email in emails:
            token = secrets.token_urlsafe(32)
            invite = ExclusiveInvite(
                token=token,
                team_id=payload.team_id,
                email=email,
                used=False,
                expires_at=datetime.utcnow() + timedelta(hours=5),
            )
            db.add(invite)
            invite_url = f"{base_url}/user/exclusive_join?token={token}"
            email_sent = await _send_exclusive_invite_email(email, invite_url, team_name, db)

            results.append({
                "email": email,
                "invite_url": invite_url,
                "email_sent": email_sent
            })

        # 发送专属邀请后，同步将候车室中对应邮箱标记为已通知，避免继续停留在等待列表
        waiting_result = await db.execute(
            select(WaitingRoom).where(WaitingRoom.notified == False)
        )
        waiting_entries = waiting_result.scalars().all()
        notified_now = datetime.utcnow()
        synced_count = 0
        email_set = set(emails)
        for entry in waiting_entries:
            entry_email = (entry.email or "").strip().lower()
            if entry_email in email_set:
                entry.notified = True
                entry.notified_at = notified_now
                synced_count += 1

        await db.commit()

        sent_count = len([r for r in results if r.get("email_sent")])
        message = f"已生成 {len(results)} 条专属链接，成功发送邮件 {sent_count} 封"
        if synced_count > 0:
            message += f"，已同步移出候车列表 {synced_count} 人"
        if sent_count == 0:
            message += "（未检测到邮件服务配置，可复制链接手动发送）"

        return JSONResponse(content={
            "success": True,
            "message": message,
            "results": results
        })

    except Exception as e:
        await db.rollback()
        logger.error(f"批量发送专属邀请失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"发送失败: {str(e)}"}
        )


@router.post("/exclusive-invite/send-priority")
async def send_exclusive_invite_priority(
    request: Request,
    payload: ExclusiveInvitePriorityRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """向所有优先候车用户发送打赏专属上车链接"""
    try:
        waiting_result = await db.execute(
            select(WaitingRoom).where(
                WaitingRoom.is_priority == True,
                WaitingRoom.notified == False
            )
        )
        entries = waiting_result.scalars().all()
        priority_emails = []
        seen = set()
        for entry in entries:
            email = (entry.email or "").strip().lower()
            if email and email not in seen:
                seen.add(email)
                priority_emails.append(email)

        if not priority_emails:
            return JSONResponse(content={
                "success": True,
                "message": "当前没有优先用户",
                "results": []
            })

        batch_payload = ExclusiveInviteBatchRequest(team_id=payload.team_id, emails=priority_emails)
        return await send_exclusive_invite_batch(request, batch_payload, db, current_user)

    except Exception as e:
        logger.error(f"发送优先用户专属邀请失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"发送失败: {str(e)}"}
        )


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    系统设置页面

    Args:
        request: FastAPI Request 对象
        db: 数据库会话
        current_user: 当前用户（需要登录）

    Returns:
        系统设置页面 HTML
    """
    try:
        from app.main import templates
        from app.services.settings import settings_service

        logger.info("管理员访问系统设置页面")

        # 获取当前配置
        proxy_config = await settings_service.get_proxy_config(db)
        log_level = await settings_service.get_log_level(db)
        external_api_config = await settings_service.get_external_api_config(db)
        email_config = await settings_service.get_email_config(db)
        idc_config = await settings_service.get_idc_config(db)
        linuxdo_oauth_config = await settings_service.get_linuxdo_oauth_config(db)
        maintenance_config = await settings_service.get_maintenance_config(db)
        warranty_days = await settings_service.get_warranty_days(db)
        announcement = await settings_service.get_announcement(db)
        shop_items = await settings_service.get_shop_items(db)
        festive_config = await settings_service.get_festive_config(db)

        return templates.TemplateResponse(
            "admin/settings/index.html",
            {
                "request": request,
                "user": current_user,
                "active_page": "settings",
                "proxy_enabled": proxy_config["enabled"],
                "proxy": proxy_config["proxy"],
                "log_level": log_level,
                "external_api_enabled": external_api_config["enabled"],
                "external_api_key": external_api_config["api_key"],
                "smtp_enabled": email_config["smtp_enabled"],
                "smtp_host": email_config["smtp_host"],
                "smtp_port": email_config["smtp_port"],
                "smtp_username": email_config["smtp_username"],
                "smtp_password": email_config["smtp_password"],
                "smtp_from_email": email_config["smtp_from_email"],
                "smtp_use_ssl": email_config["smtp_use_ssl"],
                "resend_enabled": email_config["resend_enabled"],
                "resend_api_key": email_config["resend_api_key"],
                "resend_from_email": email_config["resend_from_email"],
                "idc_enabled": idc_config.get("enabled", False),
                "idc_pid": idc_config.get("pid", ""),
                "idc_key": idc_config.get("key", ""),
                "idc_amount": idc_config.get("amount", "6.66"),
                "linuxdo_oauth_enabled": linuxdo_oauth_config.get("enabled", False),
                "linuxdo_client_id": linuxdo_oauth_config.get("client_id", ""),
                "linuxdo_client_secret": linuxdo_oauth_config.get("client_secret", ""),
                "linuxdo_authorize_url": linuxdo_oauth_config.get("authorize_url", ""),
                "linuxdo_token_url": linuxdo_oauth_config.get("token_url", ""),
                "linuxdo_userinfo_url": linuxdo_oauth_config.get("userinfo_url", ""),
                "linuxdo_scope": linuxdo_oauth_config.get("scope", "read"),
                "linuxdo_redirect_path": linuxdo_oauth_config.get("redirect_path", "/user/auth/callback"),
                "maintenance_enabled": maintenance_config.get("enabled", False),
                "maintenance_end_time": maintenance_config.get("end_time", ""),
                "maintenance_title": maintenance_config.get("title", "系统维护中"),
                "maintenance_content": maintenance_config.get("content", "系统正在维护，请稍后再试"),
                "maintenance_video_enabled": maintenance_config.get("video_enabled", False),
                "maintenance_video_embed": maintenance_config.get("video_embed", ""),
                "warranty_days": warranty_days,
                "announcement_enabled": announcement["enabled"],
                "announcement_content": announcement["content"],
                "shop_items": shop_items,
                "festive_enabled": festive_config["enabled"],
            }
        )

    except Exception as e:
        logger.error(f"获取系统设置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统设置失败: {str(e)}"
        )


class ProxyConfigRequest(BaseModel):
    """代理配置请求"""
    enabled: bool = Field(..., description="是否启用代理")
    proxy: str = Field("", description="代理地址")


class LogLevelRequest(BaseModel):
    """日志级别请求"""
    level: str = Field(..., description="日志级别")


class ExternalApiRequest(BaseModel):
    """外部API配置请求"""
    enabled: bool = Field(..., description="是否启用外部API")
    api_key: str = Field("", description="API密钥")


class WarrantyDaysRequest(BaseModel):
    """质保天数配置请求"""
    days: int = Field(..., description="质保天数", ge=1, le=3650)


class AnnouncementRequest(BaseModel):
    """公告配置请求"""
    enabled: bool = Field(False, description="是否启用公告")
    content: str = Field("", description="公告内容")


class ShopItem(BaseModel):
    key: str = Field(..., description="商品唯一标识")
    name: str = Field(..., description="商品名称")
    desc: str = Field("", description="商品描述")
    cost: int = Field(..., ge=1, description="积分消耗")
    enabled: bool = Field(True, description="是否上架")


class ShopItemsRequest(BaseModel):
    items: list[ShopItem]


class EmailConfigRequest(BaseModel):
    """邮件配置请求（兼容 SMTP / Resend 字段）"""
    smtp_enabled: Optional[bool] = Field(None, description="是否启用 SMTP")
    smtp_host: Optional[str] = Field(None, description="SMTP 主机")
    smtp_port: Optional[int] = Field(None, description="SMTP 端口")
    smtp_username: Optional[str] = Field(None, description="SMTP 用户名")
    smtp_password: Optional[str] = Field(None, description="SMTP 密码")
    smtp_from_email: Optional[str] = Field(None, description="SMTP 发件邮箱")
    smtp_use_ssl: Optional[bool] = Field(None, description="SMTP 是否使用 SSL")
    resend_enabled: Optional[bool] = Field(None, description="是否启用 Resend")
    resend_api_key: Optional[str] = Field(None, description="Resend API Key")
    resend_from_email: Optional[str] = Field(None, description="Resend 发件邮箱")


class IdcConfigRequest(BaseModel):
    """IDC 打赏配置请求"""
    enabled: bool = Field(False, description="是否启用 IDC 打赏")
    pid: str = Field("", description="商户 PID")
    key: str = Field("", description="商户密钥")
    client_id: Optional[str] = Field(None, description="兼容字段: 商户 PID")
    client_secret: Optional[str] = Field(None, description="兼容字段: 商户密钥")
    amount: str = Field("6.66", description="打赏金额")


class LinuxDoOAuthConfigRequest(BaseModel):
    """LinuxDo OAuth 配置请求"""
    enabled: bool = Field(False, description="是否启用 LinuxDo OAuth")
    client_id: str = Field("", description="OAuth Client ID")
    client_secret: str = Field("", description="OAuth Client Secret")
    authorize_url: str = Field("https://connect.linux.do/oauth2/authorize", description="授权地址")
    token_url: str = Field("https://connect.linux.do/oauth2/token", description="Token 地址")
    userinfo_url: str = Field("https://connect.linux.do/api/user", description="用户信息地址")
    scope: str = Field("read", description="授权范围")
    redirect_path: str = Field("/user/auth/callback", description="回调路径")


class MaintenanceConfigRequest(BaseModel):
    """维护模式配置请求"""
    enabled: bool = Field(False, description="是否启用维护模式")
    end_time: Optional[str] = Field("", description="维护结束时间（ISO 格式）")
    title: Optional[str] = Field("系统维护中", description="维护页面标题")
    content: Optional[str] = Field("系统正在维护，请稍后再试", description="维护页面内容")
    video_enabled: Optional[bool] = Field(False, description="是否展示维护视频")
    video_embed: Optional[str] = Field("", description="维护页面视频嵌入代码 (iframe)")


class FestiveConfigRequest(BaseModel):
    """节日装饰配置请求"""
    enabled: bool = Field(False, description="是否启用节日装饰")


@router.post("/settings/proxy")
async def update_proxy_config(
    proxy_data: ProxyConfigRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    更新代理配置

    Args:
        proxy_data: 代理配置数据
        db: 数据库会话
        current_user: 当前用户（需要登录）

    Returns:
        更新结果
    """
    try:
        from app.services.settings import settings_service

        logger.info(f"管理员更新代理配置: enabled={proxy_data.enabled}, proxy={proxy_data.proxy}")

        # 验证代理地址格式
        if proxy_data.enabled and proxy_data.proxy:
            proxy = proxy_data.proxy.strip()
            if not (
                proxy.startswith("http://")
                or proxy.startswith("https://")
                or proxy.startswith("socks5://")
                or proxy.startswith("socks5h://")
            ):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "success": False,
                        "error": "代理地址格式错误,应为 http://host:port、socks5://host:port 或 socks5h://host:port"
                    }
                )

        # 更新配置
        success = await settings_service.update_proxy_config(
            db,
            proxy_data.enabled,
            proxy_data.proxy.strip() if proxy_data.proxy else ""
        )

        if success:
            return JSONResponse(content={"success": True, "message": "代理配置已保存"})
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"success": False, "error": "保存失败"}
            )

    except Exception as e:
        logger.error(f"更新代理配置失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"更新失败: {str(e)}"}
        )


@router.post("/settings/log-level")
async def update_log_level(
    log_data: LogLevelRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    更新日志级别

    Args:
        log_data: 日志级别数据
        db: 数据库会话
        current_user: 当前用户（需要登录）

    Returns:
        更新结果
    """
    try:
        from app.services.settings import settings_service

        logger.info(f"管理员更新日志级别: {log_data.level}")

        # 更新日志级别
        success = await settings_service.update_log_level(db, log_data.level)

        if success:
            return JSONResponse(content={"success": True, "message": "日志级别已保存"})
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "error": "无效的日志级别"}
            )

    except Exception as e:
        logger.error(f"更新日志级别失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"更新失败: {str(e)}"}
        )


@router.post("/settings/external-api")
async def update_external_api_config(
    api_data: ExternalApiRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    更新外部API配置

    Args:
        api_data: 外部API配置数据
        db: 数据库会话
        current_user: 当前用户（需要登录）

    Returns:
        更新结果
    """
    try:
        from app.services.settings import settings_service

        logger.info(f"管理员更新外部API配置: enabled={api_data.enabled}")

        # 更新外部API配置
        success = await settings_service.update_external_api_config(
            db, 
            enabled=api_data.enabled, 
            api_key=api_data.api_key
        )

        if success:
            return JSONResponse(content={"success": True, "message": "外部API配置已保存"})
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "error": "保存失败"}
            )

    except Exception as e:
        logger.error(f"更新外部API配置失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"更新失败: {str(e)}"}
        )


@router.get("/settings/email")
@router.get("/settings/mail")
@router.get("/settings/smtp")
async def get_email_settings(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """读取邮件配置（兼容旧前端路径）"""
    try:
        from app.services.settings import settings_service

        config = await settings_service.get_email_config(db)
        return JSONResponse(content={"success": True, "config": config})
    except Exception as e:
        logger.error(f"读取邮件配置失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"读取失败: {str(e)}"}
        )


@router.post("/settings/email")
@router.post("/settings/mail")
@router.post("/settings/smtp")
async def update_email_settings(
    data: EmailConfigRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """保存邮件配置（兼容旧前端路径）"""
    try:
        from app.services.settings import settings_service

        current = await settings_service.get_email_config(db)
        update_data = data.model_dump(exclude_unset=True)
        merged = {**current, **update_data}

        smtp_enabled = bool(merged.get("smtp_enabled", False))
        resend_enabled = bool(merged.get("resend_enabled", False))
        smtp_host = (merged.get("smtp_host") or "").strip()
        smtp_username = (merged.get("smtp_username") or "").strip()
        smtp_password = (merged.get("smtp_password") or "").strip()
        resend_api_key = (merged.get("resend_api_key") or "").strip()
        resend_from_email = (merged.get("resend_from_email") or "").strip()

        if smtp_enabled and (not smtp_host or not smtp_username or not smtp_password):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "error": "已启用 SMTP，请完整填写 SMTP 主机/用户名/密码"}
            )

        if resend_enabled and (not resend_api_key or not resend_from_email):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "error": "已启用 Resend，请填写 API Key 和发件邮箱"}
            )

        success = await settings_service.update_email_config(db, merged)
        if not success:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"success": False, "error": "保存失败"}
            )

        return JSONResponse(content={"success": True, "message": "邮件配置已保存"})

    except Exception as e:
        logger.error(f"保存邮件配置失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"保存失败: {str(e)}"}
        )


@router.get("/settings/idc")
async def get_idc_settings(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """读取 IDC 打赏配置"""
    try:
        from app.services.settings import settings_service

        config = await settings_service.get_idc_config(db)
        return JSONResponse(content={
            "success": True,
            "enabled": config.get("enabled", False),
            "pid": config.get("pid", ""),
            "key": config.get("key", ""),
            "amount": config.get("amount", "6.66"),
            "config": config
        })
    except Exception as e:
        logger.error(f"读取 IDC 配置失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"读取失败: {str(e)}"}
        )


@router.post("/settings/idc")
async def update_idc_settings(
    data: IdcConfigRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """保存 IDC 打赏配置"""
    try:
        from app.services.settings import settings_service

        pid = (data.pid or data.client_id or "").strip()
        key = (data.key or data.client_secret or "").strip()

        try:
            amount_float = float(data.amount)
        except (TypeError, ValueError):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "error": "金额格式不正确"}
            )

        if amount_float <= 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "error": "金额必须大于 0"}
            )

        if data.enabled and (not pid or not key):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "error": "已启用 IDC，请完整填写 PID 和 KEY"}
            )

        success = await settings_service.update_idc_config(
            db,
            {
                "enabled": data.enabled,
                "pid": pid,
                "key": key,
                "amount": f"{amount_float:.2f}",
            }
        )

        if not success:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"success": False, "error": "保存失败"}
            )

        return JSONResponse(content={
            "success": True,
            "message": "IDC 配置已保存",
            "enabled": data.enabled,
            "pid": pid,
            "key": key,
            "amount": f"{amount_float:.2f}",
            "config": {
                "enabled": data.enabled,
                "pid": pid,
                "key": key,
                "amount": f"{amount_float:.2f}",
            }
        })

    except Exception as e:
        logger.error(f"保存 IDC 配置失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"保存失败: {str(e)}"}
        )


@router.get("/settings/linuxdo-oauth")
async def get_linuxdo_oauth_settings(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """读取 LinuxDo OAuth 配置"""
    try:
        from app.services.settings import settings_service

        config = await settings_service.get_linuxdo_oauth_config(db)
        return JSONResponse(content={"success": True, "config": config, **config})
    except Exception as e:
        logger.error(f"读取 LinuxDo OAuth 配置失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"读取失败: {str(e)}"}
        )


@router.post("/settings/linuxdo-oauth")
async def update_linuxdo_oauth_settings(
    data: LinuxDoOAuthConfigRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """保存 LinuxDo OAuth 配置"""
    try:
        from app.services.settings import settings_service

        authorize_url = (data.authorize_url or "").strip()
        token_url = (data.token_url or "").strip()
        userinfo_url = (data.userinfo_url or "").strip()
        scope = (data.scope or "read").strip() or "read"
        redirect_path = (data.redirect_path or "/user/auth/callback").strip() or "/user/auth/callback"
        client_id = (data.client_id or "").strip()
        client_secret = (data.client_secret or "").strip()

        if data.enabled and (not client_id or not client_secret):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "error": "启用 LinuxDo OAuth 时必须填写 Client ID 和 Client Secret"}
            )

        if not authorize_url.startswith("http") or not token_url.startswith("http") or not userinfo_url.startswith("http"):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "error": "请填写合法的 LinuxDo OAuth URL（http/https）"}
            )

        if not redirect_path.startswith("/"):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "error": "回调路径必须以 / 开头"}
            )

        config = {
            "enabled": data.enabled,
            "client_id": client_id,
            "client_secret": client_secret,
            "authorize_url": authorize_url,
            "token_url": token_url,
            "userinfo_url": userinfo_url,
            "scope": scope,
            "redirect_path": redirect_path,
        }

        success = await settings_service.update_linuxdo_oauth_config(db, config)
        if not success:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"success": False, "error": "保存失败"}
            )

        return JSONResponse(content={"success": True, "message": "LinuxDo OAuth 配置已保存", "config": config, **config})
    except Exception as e:
        logger.error(f"保存 LinuxDo OAuth 配置失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"保存失败: {str(e)}"}
        )


@router.get("/settings/maintenance")
async def get_maintenance_settings(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """读取维护模式配置"""
    try:
        from app.services.settings import settings_service

        config = await settings_service.get_maintenance_config(db)
        return JSONResponse(content={
            "success": True,
            "enabled": config.get("enabled", False),
            "end_time": config.get("end_time", ""),
            "title": config.get("title", "系统维护中"),
            "content": config.get("content", "系统正在维护，请稍后再试"),
            "config": config,
        })
    except Exception as e:
        logger.error(f"读取维护模式配置失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"读取失败: {str(e)}"}
        )


@router.post("/settings/maintenance")
async def update_maintenance_settings(
    data: MaintenanceConfigRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """保存维护模式配置"""
    try:
        from app.services.settings import settings_service

        end_time = (data.end_time or "").strip()
        title = (data.title or "系统维护中").strip()
        content = (data.content or "系统正在维护，请稍后再试").strip()
        video_enabled = bool(data.video_enabled)
        video_embed = (data.video_embed or "").strip()

        if data.enabled:
            if not end_time:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"success": False, "error": "启用维护模式时必须设置结束时间"}
                )

            try:
                parsed_end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            except ValueError:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"success": False, "error": "结束时间格式不正确"}
                )

            if parsed_end.tzinfo is not None:
                parsed_end = parsed_end.astimezone().replace(tzinfo=None)

            if parsed_end <= datetime.now():
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"success": False, "error": "结束时间必须晚于当前时间"}
                )

            end_time = parsed_end.isoformat(timespec="seconds")

        success = await settings_service.update_maintenance_config(
            db,
            {
                "enabled": data.enabled,
                "end_time": end_time,
                "title": title,
                "content": content,
                "video_enabled": video_enabled,
                "video_embed": video_embed,
            }
        )

        if not success:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"success": False, "error": "保存失败"}
            )

        return JSONResponse(content={
            "success": True,
            "message": "维护模式配置已保存",
            "enabled": data.enabled,
            "end_time": end_time,
            "title": title,
            "content": content,
            "video_enabled": video_enabled,
            "video_embed": video_embed,
            "config": {
                "enabled": data.enabled,
                "end_time": end_time,
                "title": title,
                "content": content,
                "video_enabled": video_enabled,
                "video_embed": video_embed,
            }
        })
    except Exception as e:
        logger.error(f"保存维护模式配置失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"保存失败: {str(e)}"}
        )


@router.post("/settings/warranty-days")
async def update_warranty_days(
    data: WarrantyDaysRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    更新质保天数配置

    Args:
        data: 质保天数配置数据
        db: 数据库会话
        current_user: 当前用户（需要登录）

    Returns:
        更新结果
    """
    try:
        from app.services.settings import settings_service

        logger.info(f"管理员更新质保天数: {data.days}")

        success = await settings_service.update_warranty_days(db, data.days)

        if success:
            return JSONResponse(content={"success": True, "message": f"质保天数已更新为 {data.days} 天"})
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "error": "保存失败，天数必须在 1-3650 之间"}
            )

    except Exception as e:
        logger.error(f"更新质保天数失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"更新失败: {str(e)}"}
        )


@router.post("/settings/announcement")
async def update_announcement(
    data: AnnouncementRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    更新公告配置

    Args:
        data: 公告配置数据
        db: 数据库会话
        current_user: 当前用户（需要登录）

    Returns:
        更新结果
    """
    try:
        from app.services.settings import settings_service

        logger.info(f"管理员更新公告: enabled={data.enabled}, content_length={len(data.content)}")

        success = await settings_service.update_announcement(db, data.content, data.enabled)

        if success:
            return JSONResponse(content={"success": True, "message": "公告已更新"})
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "error": "保存公告失败"}
            )

    except Exception as e:
        logger.error(f"更新公告失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"更新失败: {str(e)}"}
        )


@router.post("/settings/shop-items")
async def update_shop_items(
    payload: ShopItemsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """更新积分商城商品列表。"""
    try:
        from app.services.settings import settings_service

        items_data = [item.model_dump() for item in payload.items]
        keys = [i["key"] for i in items_data]
        if len(keys) != len(set(keys)):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "error": "商品 key 不可重复"}
            )

        success = await settings_service.update_shop_items(db, items_data)
        if success:
            return {"success": True, "message": "商城商品已保存"}
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": "保存失败"}
        )
    except Exception as exc:
        logger.error(f"更新商城商品失败: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"更新失败: {str(exc)}"}
        )


@router.post("/settings/festive")
async def update_festive_config(
    payload: FestiveConfigRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """更新节日装饰配置"""
    try:
        from app.services.settings import settings_service
        success = await settings_service.update_festive_config(
            db,
            {"enabled": payload.enabled}
        )
        if success:
            return {"success": True, "message": "节日装饰配置更新成功"}
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": "保存失败"}
        )
    except Exception as exc:
        logger.error(f"更新节日装饰配置失败: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"更新失败: {str(exc)}"}
        )
