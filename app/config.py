"""
应用配置模块
使用 Pydantic Settings 管理配置
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    app_name: str = "GPT Team 管理系统"
    app_version: str = "0.1.0"
    app_host: str = "0.0.0.0"
    app_port: int = 8008
    debug: bool = True

    # 数据库配置
    # 建议在 Docker 中使用 data 目录挂载，以避免文件挂载权限或类型问题
    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR}/data/team_manage.db"

    # 安全配置
    secret_key: str = "your-secret-key-here-change-in-production"
    admin_password: str = "admin123"

    # 日志配置
    log_level: str = "INFO"

    # 时区配置
    timezone: str = "Asia/Shanghai"

    # 代理配置
    proxy: str = ""
    proxy_enabled: bool = False

    # JWT 配置
    jwt_verify_signature: bool = False

    # 外部 API 配置 (用于油猴脚本推送账号)
    external_api_key: str = "your-api-key-change-me"
    external_api_enabled: bool = True

    # LinuxDo OAuth 配置（用户登录/注册）
    linuxdo_oauth_enabled: bool = False
    linuxdo_client_id: str = ""
    linuxdo_client_secret: str = ""
    linuxdo_authorize_url: str = "https://connect.linux.do/oauth2/authorize"
    linuxdo_token_url: str = "https://connect.linux.do/oauth2/token"
    linuxdo_userinfo_url: str = "https://connect.linux.do/api/user"
    linuxdo_scope: str = "read"
    linuxdo_redirect_path: str = "/user/auth/callback"

    # 积分配置
    user_daily_signin_points: int = 10
    shop_redeem_code_cost: int = 100

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# 创建全局配置实例
settings = Settings()
