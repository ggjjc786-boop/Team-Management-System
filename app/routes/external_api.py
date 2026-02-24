"""
外部 API 路由
提供给油猴脚本等外部工具推送账号的接口
"""
import asyncio
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, AsyncSessionLocal
from app.config import settings
from app.services.team import TeamService
from app.services.settings import settings_service

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(
    prefix="/external",
    tags=["external"]
)

# 服务实例
team_service = TeamService()


class PushAccountRequest(BaseModel):
    """推送账号请求模型"""
    access_token: str = Field(..., description="ChatGPT Access Token")
    email: Optional[str] = Field(None, description="账号邮箱 (可选，会自动从Token提取)")
    password: Optional[str] = Field(None, description="账号密码 (可选，仅作记录)")
    account_id: Optional[str] = Field(None, description="指定 Account ID (可选)")


class PushAccountResponse(BaseModel):
    """推送账号响应模型"""
    success: bool
    message: str
    team_id: Optional[int] = None
    error: Optional[str] = None


def verify_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    """
    验证 API 密钥 (同步版本，使用配置文件)
    
    Args:
        x_api_key: 请求头中的 API 密钥
        
    Returns:
        True 如果验证通过
        
    Raises:
        HTTPException: 如果验证失败
    """
    if not settings.external_api_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="外部 API 未启用"
        )
    
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少 API 密钥，请在请求头中提供 X-API-Key"
        )
    
    if x_api_key != settings.external_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API 密钥无效"
        )
    
    return True


async def verify_api_key_async(
    x_api_key: str = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db)
):
    """
    验证 API 密钥 (异步版本，从数据库读取配置)
    
    Args:
        x_api_key: 请求头中的 API 密钥
        db: 数据库会话
        
    Returns:
        True 如果验证通过
        
    Raises:
        HTTPException: 如果验证失败
    """
    # 从数据库获取配置
    config = await settings_service.get_external_api_config(db)
    
    if not config["enabled"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="外部 API 未启用"
        )
    
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少 API 密钥，请在请求头中提供 X-API-Key"
        )
    
    if x_api_key != config["api_key"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API 密钥无效"
        )
    
    return True


async def _background_refresh(team_id: int):
    """
    后台异步刷新 Team 信息（成员数、状态等）
    使用独立的数据库会话，不依赖请求生命周期
    """
    async with AsyncSessionLocal() as db:
        try:
            sync_result = await team_service.sync_team_info(team_id, db)
            if sync_result["success"]:
                logger.info(f"后台自动刷新成功: team_id={team_id}")
            else:
                logger.warning(f"后台自动刷新失败: team_id={team_id}, error={sync_result.get('error')}")
        except Exception as e:
            logger.error(f"后台刷新异常: team_id={team_id}, error={e}")


@router.post("/push", response_model=PushAccountResponse)
async def push_account(
    request: PushAccountRequest,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_api_key_async)
):
    """
    推送账号到系统
    
    同步导入账号（确保入库成功再返回），导入成功后后台异步刷新 Team 信息。
    
    Args:
        request: 推送请求，包含 access_token, email, password 等
        db: 数据库会话
        
    Returns:
        推送结果
    """
    logger.info(f"收到外部推送请求: email={request.email or '(从Token提取)'}")

    try:
        # 同步导入，确保数据库写入成功再返回
        result = await team_service.import_team_single(
            access_token=request.access_token,
            db_session=db,
            email=request.email,
            account_id=request.account_id
        )

        if not result["success"]:
            logger.warning(f"推送导入失败: {result.get('error')}")
            return PushAccountResponse(
                success=False,
                message=result.get("error", "导入失败"),
                team_id=result.get("team_id"),
                error=result.get("error")
            )

        team_id = result.get("team_id")
        logger.info(f"推送导入成功: team_id={team_id}")

        # 导入成功后，后台异步刷新 Team 详细信息（不阻塞响应）
        if team_id:
            asyncio.create_task(_background_refresh(team_id))

        return PushAccountResponse(
            success=True,
            message=result.get("message", "导入成功"),
            team_id=team_id
        )

    except Exception as e:
        logger.error(f"推送处理异常: {e}")
        return PushAccountResponse(
            success=False,
            message=f"推送处理异常: {str(e)}",
            error=str(e)
        )


@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_api_key_async)
):
    """
    健康检查接口
    
    用于验证 API 密钥是否有效以及服务是否正常运行
    
    Returns:
        健康状态
    """
    config = await settings_service.get_external_api_config(db)
    return JSONResponse(content={
        "status": "ok",
        "message": "外部 API 服务正常",
        "api_enabled": config["enabled"]
    })


@router.get("/public/status")
async def public_status():
    """
    公开状态检查接口 (无需 API Key)
    
    用于油猴脚本检测服务是否可用
    
    Returns:
        服务状态
    """
    return JSONResponse(content={
        "status": "ok",
        "message": "Team 管理系统在线"
    })


@router.post("/push/batch")
async def push_accounts_batch(
    accounts: list[PushAccountRequest],
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_api_key_async)
):
    """
    批量推送账号
    
    Args:
        accounts: 账号列表
        db: 数据库会话
        
    Returns:
        批量推送结果
    """
    results = []
    success_count = 0
    fail_count = 0
    
    for account in accounts:
        try:
            result = await team_service.import_team_single(
                access_token=account.access_token,
                db_session=db,
                email=account.email,
                account_id=account.account_id
            )
            
            if result["success"]:
                success_count += 1
            else:
                fail_count += 1
                
            results.append({
                "email": account.email or "(从Token提取)",
                "success": result["success"],
                "team_id": result.get("team_id"),
                "error": result.get("error")
            })
            
        except Exception as e:
            fail_count += 1
            results.append({
                "email": account.email or "(从Token提取)",
                "success": False,
                "error": str(e)
            })
    
    return JSONResponse(content={
        "success": fail_count == 0,
        "message": f"批量推送完成: {success_count} 成功, {fail_count} 失败",
        "total": len(accounts),
        "success_count": success_count,
        "fail_count": fail_count,
        "results": results
    })
