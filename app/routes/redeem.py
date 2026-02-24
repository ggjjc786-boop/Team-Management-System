"""
兑换路由
处理用户兑换码验证和加入 Team 的请求
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import PlainTextResponse, RedirectResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.redeem_flow import redeem_flow_service
from app.models import ExclusiveInvite, Team
from app.services.team import team_service
from app.services.waiting_room import waiting_room_service
from app.services.idc_payment import idc_payment_service

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(
    prefix="/redeem",
    tags=["redeem"]
)


# 请求模型
class VerifyCodeRequest(BaseModel):
    """验证兑换码请求"""
    code: str = Field(..., description="兑换码", min_length=1)


class RedeemRequest(BaseModel):
    """兑换请求"""
    email: EmailStr = Field(..., description="用户邮箱")
    code: str = Field(..., description="兑换码", min_length=1)
    team_id: Optional[int] = Field(None, description="Team ID (可选，不提供则自动选择)")


class WarrantyQueryRequest(BaseModel):
    """质保查询请求"""
    code: str = Field(..., description="兑换码", min_length=1)


class WarrantyRedeemRequest(BaseModel):
    """质保重新兑换请求"""
    email: EmailStr = Field(..., description="用户邮箱")
    code: str = Field(..., description="兑换码", min_length=1)


class ExclusiveJoinRequest(BaseModel):
    """专属链接上车请求"""
    token: str = Field(..., description="邀请令牌", min_length=8)
    email: EmailStr = Field(..., description="用户邮箱")


class FreeSpotJoinRequest(BaseModel):
    """免费车位上车请求"""
    email: EmailStr = Field(..., description="用户邮箱")
    team_id: int = Field(..., description="Team ID")


class WaitingRoomJoinRequest(BaseModel):
    """加入候车室请求"""
    email: EmailStr = Field(..., description="用户邮箱")


class IdcCreateOrderRequest(BaseModel):
    """创建 IDC 打赏订单请求"""
    email: EmailStr = Field(..., description="用户邮箱")


# 响应模型
class TeamInfo(BaseModel):
    """Team 信息"""
    id: int
    team_name: str
    current_members: int
    max_members: int
    expires_at: Optional[str]
    subscription_plan: Optional[str]


class VerifyCodeResponse(BaseModel):
    """验证兑换码响应"""
    success: bool
    valid: bool
    reason: Optional[str] = None
    teams: List[TeamInfo] = []
    error: Optional[str] = None


class RedeemResponse(BaseModel):
    """兑换响应"""
    success: bool
    message: Optional[str] = None
    team_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/verify", response_model=VerifyCodeResponse)
async def verify_code(
    request: VerifyCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    验证兑换码并返回可用 Team 列表

    Args:
        request: 验证请求
        db: 数据库会话

    Returns:
        验证结果和可用 Team 列表
    """
    try:
        logger.info(f"验证兑换码请求: {request.code}")

        result = await redeem_flow_service.verify_code_and_get_teams(
            request.code,
            db
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )

        return VerifyCodeResponse(
            success=result["success"],
            valid=result["valid"],
            reason=result["reason"],
            teams=[TeamInfo(**team) for team in result["teams"]],
            error=result["error"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"验证兑换码失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证失败: {str(e)}"
        )


@router.post("/confirm", response_model=RedeemResponse)
async def confirm_redeem(
    request: RedeemRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    确认兑换并加入 Team

    Args:
        request: 兑换请求
        db: 数据库会话

    Returns:
        兑换结果
    """
    try:
        logger.info(f"兑换请求: {request.email} -> Team {request.team_id} (兑换码: {request.code})")

        result = await redeem_flow_service.redeem_and_join_team(
            request.email,
            request.code,
            request.team_id,
            db
        )

        if not result["success"]:
            error_msg = result.get("error") or result.get("message") or "兑换失败"
            # 根据错误类型返回不同的状态码
            if "不存在" in error_msg or "已使用" in error_msg or "已过期" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
            elif "已满" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=error_msg
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_msg
                )

        return RedeemResponse(
            success=result["success"],
            message=result["message"],
            team_info=result["team_info"],
            error=result["error"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"兑换失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"兑换失败: {str(e)}"
        )


@router.post("/warranty/query")
async def warranty_query(
    request: WarrantyQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    质保查询：检查兑换码是否支持质保重新兑换
    """
    try:
        result = await redeem_flow_service.warranty_query(request.code, db)
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"质保查询失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询失败: {str(e)}"
        )


@router.post("/warranty/redeem")
async def warranty_redeem(
    request: WarrantyRedeemRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    质保重新兑换：封号后使用原兑换码重新加入 Team
    """
    try:
        result = await redeem_flow_service.warranty_redeem(
            request.email,
            request.code,
            db
        )
        if not result["success"]:
            status_code = status.HTTP_400_BAD_REQUEST
            if "过期" in result.get("error", "") or "超出" in result.get("error", ""):
                status_code = status.HTTP_400_BAD_REQUEST
            elif "已满" in result.get("error", ""):
                status_code = status.HTTP_409_CONFLICT
            raise HTTPException(status_code=status_code, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"质保兑换失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"质保兑换失败: {str(e)}"
        )


@router.post("/exclusive-join")
async def exclusive_join(
    request: ExclusiveJoinRequest,
    db: AsyncSession = Depends(get_db)
):
    """通过打赏专属链接上车"""
    try:
        token = request.token.strip()
        email = request.email.strip().lower()

        invite_result = await db.execute(
            select(ExclusiveInvite).where(ExclusiveInvite.token == token)
        )
        invite = invite_result.scalar_one_or_none()
        if not invite:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="邀请链接不存在或已失效")

        if invite.used:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该专属链接已被使用")

        if invite.expires_at and invite.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该专属链接已过期")

        if invite.email.strip().lower() != email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱与邀请链接不匹配")

        team_result = await db.execute(select(Team).where(Team.id == invite.team_id))
        team = team_result.scalar_one_or_none()
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="目标 Team 不存在")

        if team.status in ("expired", "error"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前 Team 不可用")

        if team.current_members >= team.max_members:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="当前 Team 车位已满")

        join_result = await team_service.add_team_member(team.id, email, db)
        if not join_result.get("success"):
            error_msg = join_result.get("error") or "上车失败"
            status_code = status.HTTP_409_CONFLICT if "已满" in error_msg else status.HTTP_400_BAD_REQUEST
            raise HTTPException(status_code=status_code, detail=error_msg)

        invite.used = True
        invite.used_at = datetime.utcnow()
        await db.commit()

        return {
            "success": True,
            "message": "上车成功，请查收邀请邮件",
            "team_info": {
                "id": team.id,
                "team_name": team.team_name,
                "current_members": team.current_members,
                "max_members": team.max_members,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"专属上车失败: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上车失败: {str(e)}"
        )


@router.get("/free-spots")
async def get_free_spots(db: AsyncSession = Depends(get_db)):
    """获取可上车的免费 Team 列表"""
    try:
        result = await team_service.get_free_spot_teams(db)
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error") or "获取免费车位失败"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取免费车位失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取免费车位失败: {str(e)}"
        )


@router.post("/free-spot/join")
async def join_free_spot(request: FreeSpotJoinRequest, db: AsyncSession = Depends(get_db)):
    """加入指定免费车位 Team"""
    try:
        team_result = await db.execute(select(Team).where(Team.id == request.team_id))
        team = team_result.scalar_one_or_none()

        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team 不存在")
        if team.status in ("expired", "error"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前 Team 不可用")
        if not team.is_free_spot:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该 Team 不是免费车位")
        if team.is_exclusive:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该 Team 为打赏专属，无法直接上车")
        if team.current_members >= team.max_members:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="当前 Team 车位已满")

        join_result = await team_service.add_team_member(team.id, request.email, db)
        if not join_result.get("success"):
            error_msg = join_result.get("error") or "上车失败"
            status_code = status.HTTP_409_CONFLICT if "已满" in error_msg else status.HTTP_400_BAD_REQUEST
            raise HTTPException(status_code=status_code, detail=error_msg)

        return {
            "success": True,
            "message": "上车成功，请查收邀请邮件",
            "team_info": {
                "id": team.id,
                "team_name": team.team_name,
                "current_members": team.current_members,
                "max_members": team.max_members,
                "expires_at": team.expires_at.isoformat() if team.expires_at else None,
                "subscription_plan": team.subscription_plan,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"免费车位上车失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上车失败: {str(e)}"
        )


@router.get("/waiting-room/count")
async def waiting_room_count(db: AsyncSession = Depends(get_db)):
    """获取候车室人数"""
    try:
        count = await waiting_room_service.get_waiting_count(db)
        return {"success": True, "count": count}
    except Exception as e:
        logger.error(f"获取候车室人数失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取候车人数失败: {str(e)}"
        )


@router.post("/waiting-room/join")
async def waiting_room_join(request: WaitingRoomJoinRequest, db: AsyncSession = Depends(get_db)):
    """加入候车室"""
    try:
        result = await waiting_room_service.join(db, request.email)
        if not result.get("success"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("message") or "加入失败")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"加入候车室失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"加入候车室失败: {str(e)}"
        )


@router.post("/idc/create-order")
async def create_idc_order(
    request: IdcCreateOrderRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """创建 IDC 打赏订单"""
    try:
        site_url = str(http_request.base_url).rstrip("/")
        result = await idc_payment_service.create_order(request.email, db, site_url)
        if not result.get("success"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error") or "创建订单失败")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建 IDC 订单失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建订单失败: {str(e)}"
        )


@router.get("/idc/order-status")
async def idc_order_status(out_trade_no: str, db: AsyncSession = Depends(get_db)):
    """查询 IDC 订单状态（优先本地，必要时远程同步）"""
    try:
        result = await idc_payment_service.query_order(out_trade_no, db)
        if result.get("success") and result.get("status") == "paid":
            return result

        # 本地未支付时尝试远程同步，减少回调延迟带来的前端等待
        remote_result = await idc_payment_service.query_order_remote(out_trade_no, db)
        if remote_result.get("success"):
            return remote_result

        return result
    except Exception as e:
        logger.error(f"查询 IDC 订单状态失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询订单失败: {str(e)}"
        )


@router.post("/idc/notify", response_class=PlainTextResponse)
@router.get("/idc/notify", response_class=PlainTextResponse)
async def idc_notify(http_request: Request, db: AsyncSession = Depends(get_db)):
    """IDC 异步回调"""
    try:
        if http_request.method.upper() == "POST":
            form = await http_request.form()
            params = dict(form)
        else:
            params = dict(http_request.query_params)

        result = await idc_payment_service.handle_notify(params, db)
        return PlainTextResponse(result)
    except Exception as e:
        logger.error(f"IDC 回调处理失败: {e}")
        return PlainTextResponse("fail")


@router.get("/idc/return")
async def idc_return(out_trade_no: Optional[str] = None, trade_status: Optional[str] = None):
    """IDC 前端回跳地址，重定向到候车室页面用于前端轮询确认"""
    paid = "1" if trade_status == "TRADE_SUCCESS" else "0"
    if out_trade_no:
        return RedirectResponse(url=f"/waiting-room?paid={paid}&order={out_trade_no}")
    return RedirectResponse(url=f"/waiting-room?paid={paid}")
