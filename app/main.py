"""
GPT Team 管理和兑换码自动邀请系统
FastAPI 应用入口文件
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from starlette.middleware.sessions import SessionMiddleware
import logging
import time
import asyncio
from collections import defaultdict
from pathlib import Path
from datetime import datetime

from contextlib import asynccontextmanager
# 导入路由
from app.routes import redeem, auth, admin, api, user, external_api, linuxdo
from app.config import settings
from app.database import init_db, close_db, AsyncSessionLocal
from app.services.auth import auth_service

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"

from starlette.exceptions import HTTPException as StarletteHTTPException

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库，关闭时释放资源
    """
    logger.info("系统正在启动，正在初始化数据库...")
    try:
        # 0. 确保数据库目录存在
        db_file = settings.database_url.split("///")[-1]
        Path(db_file).parent.mkdir(parents=True, exist_ok=True)
        
        # 1. 创建数据库表
        await init_db()
        # 2. 初始化管理员密码（如果不存在）
        async with AsyncSessionLocal() as session:
            await auth_service.initialize_admin_password(session)
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
    
    yield
    
    # 关闭连接
    await close_db()
    logger.info("系统正在关闭，已释放数据库连接")


# 创建 FastAPI 应用实例
app = FastAPI(
    title="GPT Team 管理系统",
    description="ChatGPT Team 账号管理和兑换码自动邀请系统",
    version="0.1.0",
    lifespan=lifespan
)

# 全局异常处理
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """ 处理 HTTP 异常 """
    if exc.status_code in [401, 403]:
        # 检查是否是 HTML 请求
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            return RedirectResponse(url="/login")
    
    # 默认返回 JSON 响应（FastAPI 的默认行为）
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# 配置 Session 中间件
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="session",
    max_age=14 * 24 * 60 * 60,  # 14 天
    same_site="lax",
    https_only=False  # 开发环境设为 False，生产环境应设为 True
)


# ===== 安全中间件 =====

# IP 请求频率限制器（内存存储，滑动窗口）
class RateLimiter:
    """基于 IP 的请求频率限制器"""
    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self._requests: dict = defaultdict(list)

    def is_limited(self, ip: str) -> bool:
        now = time.time()
        cutoff = now - self.window
        # 清理过期记录
        self._requests[ip] = [t for t in self._requests[ip] if t > cutoff]
        if len(self._requests[ip]) >= self.max_requests:
            return True
        self._requests[ip].append(now)
        return False

# 兑换接口专属限流器（更严格：60秒内最多20次）
_redeem_limiter = RateLimiter(max_requests=20, window_seconds=60)

# 敏感响应 Header 黑名单
_STRIP_HEADERS = {
    "server", "x-powered-by", "req-cost-time", "req-arrive-time",
    "x-aspnet-version", "x-aspnetmvc-version",
}

_MAINTENANCE_EXEMPT_PREFIXES = (
    "/admin",
    "/auth",
    "/login",
    "/static",
    "/health",
    "/favicon.ico",
    "/docs",
    "/openapi.json",
    "/redoc",
)


def _is_maintenance_exempt(path: str) -> bool:
    if path == "/":
        return False
    return any(path.startswith(prefix) for prefix in _MAINTENANCE_EXEMPT_PREFIXES)


def _is_admin_user(request: Request) -> bool:
    session_data = request.scope.get("session")
    user = session_data.get("user") if isinstance(session_data, dict) else None
    return bool(user and user.get("is_admin"))


@app.middleware("http")
async def maintenance_middleware(request: Request, call_next):
    path = request.url.path

    if _is_maintenance_exempt(path) or _is_admin_user(request):
        return await call_next(request)

    try:
        from app.services.settings import settings_service

        async with AsyncSessionLocal() as session:
            config = await settings_service.get_maintenance_config(session)
    except Exception as exc:
        logger.error(f"读取维护模式配置失败: {exc}")
        return await call_next(request)

    if not config.get("enabled", False):
        return await call_next(request)

    end_time_raw = config.get("end_time", "")
    end_time = None
    if end_time_raw:
        try:
            end_time = datetime.fromisoformat(end_time_raw.replace("Z", "+00:00"))
            if end_time.tzinfo is not None:
                end_time = end_time.astimezone().replace(tzinfo=None)
        except ValueError:
            end_time = None

    remaining_seconds = None
    if end_time:
        remaining_seconds = int((end_time - datetime.now()).total_seconds())
        if remaining_seconds <= 0:
            return await call_next(request)

    accepts_html = "text/html" in request.headers.get("accept", "")
    if accepts_html:
        return templates.TemplateResponse(
            "maintenance.html",
            {
                "request": request,
                "title": config.get("title", "系统维护中"),
                "content": config.get("content", "系统正在维护，请稍后再试"),
                "end_time": end_time.isoformat() if end_time else "",
                "remaining_seconds": max(0, remaining_seconds) if remaining_seconds is not None else None,
                "video_enabled": config.get("video_enabled", False),
                "video_embed": config.get("video_embed", ""),
            },
            status_code=503,
        )

    return JSONResponse(
        status_code=503,
        content={
            "detail": "系统维护中",
            "title": config.get("title", "系统维护中"),
            "content": config.get("content", "系统正在维护，请稍后再试"),
            "end_time": end_time.isoformat() if end_time else "",
            "remaining_seconds": max(0, remaining_seconds) if remaining_seconds is not None else None,
            "video_enabled": config.get("video_enabled", False),
            "video_embed": config.get("video_embed", ""),
        }
    )


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """
    安全中间件：
    1. 对兑换接口进行 IP 频率限制
    2. 剥离敏感响应头
    3. 添加安全响应头
    """
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or \
                request.headers.get("x-real-ip", "") or \
                (request.client.host if request.client else "unknown")

    # 对 /redeem 路径进行速率限制
    if request.url.path.startswith("/redeem"):
        if _redeem_limiter.is_limited(client_ip):
            logger.warning(f"速率限制触发: IP={client_ip} path={request.url.path}")
            return JSONResponse(
                status_code=429,
                content={"detail": "请求过于频繁，请稍后再试"},
                headers={"Retry-After": "60"}
            )

    response = await call_next(request)

    # 剥离敏感响应头
    for header in _STRIP_HEADERS:
        if header in response.headers:
            del response.headers[header]

    # 添加安全响应头
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"

    return response

# 配置静态文件
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")

# 配置模板引擎
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))

# 添加模板过滤器
def format_datetime(dt):
    """格式化日期时间"""
    if not dt:
        return "-"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("+00:00", ""))
        except:
            return dt
    return dt.strftime("%Y-%m-%d %H:%M")

def escape_js(value):
    """转义字符串用于 JavaScript"""
    if not value:
        return ""
    return value.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")

templates.env.filters["format_datetime"] = format_datetime
templates.env.filters["escape_js"] = escape_js

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 注册路由
app.include_router(user.router)  # 用户路由(根路径)
app.include_router(redeem.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(api.router)
app.include_router(external_api.router)  # 外部 API (油猴脚本)
app.include_router(linuxdo.router)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """登录页面"""
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "user": None}
    )


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """浏览器会自动请求 favicon，显式返回空内容避免 404 噪音"""
    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )
