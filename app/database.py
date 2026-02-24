"""
数据库连接模块
SQLite 异步连接配置和会话管理
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# 创建异步引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # 开发环境打印 SQL
    future=True
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# 创建 Base 类
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    获取数据库会话
    用于 FastAPI 依赖注入
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    初始化数据库
    创建所有表，并对已有表执行增量列迁移
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 增量迁移：为已有表添加质保相关字段
    async with engine.begin() as conn:
        migrations = [
            ("redemption_codes", "is_warranty", "BOOLEAN DEFAULT 0"),
            ("redemption_codes", "warranty_count", "INTEGER DEFAULT 0"),
            ("redemption_codes", "warranty_days", "INTEGER"),
            ("redemption_codes", "is_shop_sold", "BOOLEAN DEFAULT 0"),
            ("redemption_codes", "shop_sold_to_user_id", "INTEGER"),
            ("redemption_codes", "shop_sold_at", "DATETIME"),
            ("redemption_records", "is_warranty_redeem", "BOOLEAN DEFAULT 0"),
            ("teams", "is_free_spot", "BOOLEAN DEFAULT 0"),
            ("teams", "is_exclusive", "BOOLEAN DEFAULT 0"),
            ("waiting_room", "is_priority", "BOOLEAN DEFAULT 0"),
            ("waiting_room", "idc_order_no", "VARCHAR(64)"),
        ]
        for table, column, col_type in migrations:
            try:
                await conn.execute(text(
                    f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"
                ))
                logger.info(f"迁移：已添加 {table}.{column}")
            except Exception:
                # 列已存在，忽略
                pass


async def close_db():
    """
    关闭数据库连接
    """
    await engine.dispose()
