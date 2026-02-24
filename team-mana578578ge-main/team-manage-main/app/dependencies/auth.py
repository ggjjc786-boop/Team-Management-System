"""
认证依赖
用于保护需要认证的路由
"""
import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse

logger = logging.getLogger(__name__)


def get_current_user(request: Request) -> dict:
    """
    获取当前登录用户
    从 Session 中获取用户信息

    Args:
        request: FastAPI Request 对象

    Returns:
        用户信息字典

    Raises:
        HTTPException: 如果未登录
    """
    user = request.session.get("user")

    if not user:
        logger.warning("未登录用户尝试访问受保护资源")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录"
        )

    return user


def require_admin(request: Request) -> dict:
    """
    要求管理员权限
    检查用户是否已登录且具有管理员权限

    Args:
        request: FastAPI Request 对象

    Returns:
        用户信息字典

    Raises:
        HTTPException: 如果未登录或无权限
    """
    user = request.session.get("user")

    if not user:
        logger.warning("未登录用户尝试访问管理员资源")
        # 抛出 401 异常，由 app/main.py 中的全局异常处理程序处理
        # 如果是 HTML 请求会重定向到登录页，否则返回 JSON
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录，请先登录"
        )

    # 检查是否是管理员
    if not user.get("is_admin"):
        logger.warning(f"非管理员用户尝试访问管理员资源: {user.get('username')}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问"
        )

    return user


def optional_user(request: Request) -> dict | None:
    """
    可选的用户信息
    如果已登录则返回用户信息，否则返回 None

    Args:
        request: FastAPI Request 对象

    Returns:
        用户信息字典或 None
    """
    return request.session.get("user")
