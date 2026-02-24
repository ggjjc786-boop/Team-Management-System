"""
系统设置服务
管理系统配置的读取、更新和缓存
"""
from typing import Optional, Dict, Any, List
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Setting
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class SettingsService:
    """系统设置服务类"""

    def __init__(self):
        self._cache: Dict[str, str] = {}

    async def get_setting(self, session: AsyncSession, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取单个配置项

        Args:
            session: 数据库会话
            key: 配置项键名
            default: 默认值

        Returns:
            配置项值,如果不存在则返回默认值
        """
        # 先从缓存获取
        if key in self._cache:
            return self._cache[key]

        # 从数据库获取
        result = await session.execute(
            select(Setting).where(Setting.key == key)
        )
        setting = result.scalar_one_or_none()

        if setting:
            self._cache[key] = setting.value
            return setting.value

        return default

    async def get_all_settings(self, session: AsyncSession) -> Dict[str, str]:
        """
        获取所有配置项

        Args:
            session: 数据库会话

        Returns:
            配置项字典
        """
        result = await session.execute(select(Setting))
        settings = result.scalars().all()

        settings_dict = {s.key: s.value for s in settings}
        self._cache.update(settings_dict)

        return settings_dict

    async def update_setting(self, session: AsyncSession, key: str, value: str) -> bool:
        """
        更新单个配置项

        Args:
            session: 数据库会话
            key: 配置项键名
            value: 配置项值

        Returns:
            是否更新成功
        """
        try:
            result = await session.execute(
                select(Setting).where(Setting.key == key)
            )
            setting = result.scalar_one_or_none()

            if setting:
                setting.value = value
            else:
                setting = Setting(key=key, value=value)
                session.add(setting)

            await session.commit()

            # 更新缓存
            self._cache[key] = value

            logger.info(f"配置项 {key} 已更新")
            return True

        except Exception as e:
            logger.error(f"更新配置项 {key} 失败: {e}")
            await session.rollback()
            return False

    async def update_settings(self, session: AsyncSession, settings: Dict[str, str]) -> bool:
        """
        批量更新配置项

        Args:
            session: 数据库会话
            settings: 配置项字典

        Returns:
            是否更新成功
        """
        try:
            for key, value in settings.items():
                result = await session.execute(
                    select(Setting).where(Setting.key == key)
                )
                setting = result.scalar_one_or_none()

                if setting:
                    setting.value = value
                else:
                    setting = Setting(key=key, value=value)
                    session.add(setting)

            await session.commit()

            # 更新缓存
            self._cache.update(settings)

            logger.info(f"批量更新了 {len(settings)} 个配置项")
            return True

        except Exception as e:
            logger.error(f"批量更新配置项失败: {e}")
            await session.rollback()
            return False

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        logger.info("配置缓存已清空")

    async def get_shop_items(self, session: AsyncSession) -> List[Dict[str, Any]]:
        """获取积分商城商品列表，存储在 settings.shop_items(JSON)。"""
        raw = await self.get_setting(session, "shop_items", "")
        items: List[Dict[str, Any]] = []
        if raw:
            try:
                items = json.loads(raw)
            except Exception as exc:
                logger.error(f"解析 shop_items 配置失败: {exc}")
                items = []

        # 默认商品：兑换码
        if not items:
            items = [
                {
                    "key": "redeem_code",
                    "name": "GPT Team 兑换码",
                    "desc": "消耗积分获取兑换码",
                    "cost": int(settings.shop_redeem_code_cost),
                    "enabled": True,
                }
            ]
        return items

    async def update_shop_items(self, session: AsyncSession, items: List[Dict[str, Any]]) -> bool:
        """保存积分商城商品配置。"""
        try:
            value = json.dumps(items, ensure_ascii=False)
            return await self.update_setting(session, "shop_items", value)
        except Exception as exc:
            logger.error(f"保存 shop_items 失败: {exc}")
            return False

    async def get_proxy_config(self, session: AsyncSession) -> Dict[str, str]:
        """
        获取代理配置

        Returns:
            代理配置字典
        """
        proxy_enabled = await self.get_setting(session, "proxy_enabled", "false")
        proxy = await self.get_setting(session, "proxy", "")

        return {
            "enabled": proxy_enabled.lower() == "true",
            "proxy": proxy
        }

    async def update_proxy_config(
        self,
        session: AsyncSession,
        enabled: bool,
        proxy: str = ""
    ) -> bool:
        """
        更新代理配置

        Args:
            session: 数据库会话
            enabled: 是否启用代理
            proxy: 代理地址 (格式: http://host:port 或 socks5://host:port)

        Returns:
            是否更新成功
        """
        settings = {
            "proxy_enabled": str(enabled).lower(),
            "proxy": proxy
        }

        return await self.update_settings(session, settings)

    async def get_log_level(self, session: AsyncSession) -> str:
        """
        获取日志级别

        Returns:
            日志级别
        """
        return await self.get_setting(session, "log_level", "INFO")

    async def update_log_level(self, session: AsyncSession, level: str) -> bool:
        """
        更新日志级别

        Args:
            session: 数据库会话
            level: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)

        Returns:
            是否更新成功
        """
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level.upper() not in valid_levels:
            logger.error(f"无效的日志级别: {level}")
            return False

        success = await self.update_setting(session, "log_level", level.upper())

        if success:
            # 动态更新日志级别
            logging.getLogger().setLevel(level.upper())
            logger.info(f"日志级别已更新为: {level.upper()}")

        return success

    async def get_warranty_days(self, session: AsyncSession) -> int:
        """
        获取质保天数

        Returns:
            质保天数（默认30天）
        """
        val = await self.get_setting(session, "warranty_days", "30")
        try:
            return max(1, int(val))
        except (ValueError, TypeError):
            return 30

    async def update_warranty_days(self, session: AsyncSession, days: int) -> bool:
        """
        更新质保天数

        Args:
            session: 数据库会话
            days: 质保天数

        Returns:
            是否更新成功
        """
        if days < 1 or days > 3650:
            logger.error(f"无效的质保天数: {days}")
            return False
        return await self.update_setting(session, "warranty_days", str(days))

    async def get_external_api_config(self, session: AsyncSession) -> Dict[str, any]:
        """
        获取外部API配置

        Returns:
            外部API配置字典
        """
        from app.config import settings as app_settings
        
        # 优先从数据库读取，如果没有则使用配置文件默认值
        enabled = await self.get_setting(session, "external_api_enabled")
        api_key = await self.get_setting(session, "external_api_key")

        return {
            "enabled": enabled.lower() == "true" if enabled else app_settings.external_api_enabled,
            "api_key": api_key if api_key else app_settings.external_api_key
        }

    async def update_external_api_config(
        self,
        session: AsyncSession,
        enabled: bool,
        api_key: str = ""
    ) -> bool:
        """
        更新外部API配置

        Args:
            session: 数据库会话
            enabled: 是否启用外部API
            api_key: API密钥

        Returns:
            是否更新成功
        """
        from app.config import settings as app_settings
        
        settings_to_update = {
            "external_api_enabled": str(enabled).lower(),
            "external_api_key": api_key
        }

        success = await self.update_settings(session, settings_to_update)
        
        if success:
            # 动态更新配置
            app_settings.external_api_enabled = enabled
            app_settings.external_api_key = api_key
            logger.info(f"外部API配置已更新: enabled={enabled}")

        return success

    async def get_email_config(self, session: AsyncSession) -> Dict[str, Any]:
        """获取邮件发送配置（SMTP + Resend）"""
        smtp_enabled = await self.get_setting(session, "smtp_enabled", "false")
        smtp_host = await self.get_setting(session, "smtp_host", "")
        smtp_port_raw = await self.get_setting(session, "smtp_port", "465")
        smtp_username = await self.get_setting(session, "smtp_username", "")
        smtp_password = await self.get_setting(session, "smtp_password", "")
        smtp_from_email = await self.get_setting(session, "smtp_from_email", "")
        smtp_use_ssl = await self.get_setting(session, "smtp_use_ssl", "true")

        resend_enabled = await self.get_setting(session, "resend_enabled", "false")
        resend_api_key = await self.get_setting(session, "resend_api_key", "")
        resend_from_email = await self.get_setting(session, "resend_from_email", "")

        try:
            smtp_port = int(smtp_port_raw or "465")
        except (ValueError, TypeError):
            smtp_port = 465

        return {
            "smtp_enabled": (smtp_enabled or "false").lower() == "true",
            "smtp_host": smtp_host or "",
            "smtp_port": smtp_port,
            "smtp_username": smtp_username or "",
            "smtp_password": smtp_password or "",
            "smtp_from_email": smtp_from_email or "",
            "smtp_use_ssl": (smtp_use_ssl or "true").lower() == "true",
            "resend_enabled": (resend_enabled or "false").lower() == "true",
            "resend_api_key": resend_api_key or "",
            "resend_from_email": resend_from_email or "",
        }

    async def update_email_config(self, session: AsyncSession, config: Dict[str, Any]) -> bool:
        """更新邮件发送配置（SMTP + Resend）"""
        smtp_port = config.get("smtp_port", 465)
        try:
            smtp_port = int(smtp_port)
        except (ValueError, TypeError):
            smtp_port = 465

        settings_to_update = {
            "smtp_enabled": str(bool(config.get("smtp_enabled", False))).lower(),
            "smtp_host": str(config.get("smtp_host", "") or "").strip(),
            "smtp_port": str(smtp_port),
            "smtp_username": str(config.get("smtp_username", "") or "").strip(),
            "smtp_password": str(config.get("smtp_password", "") or "").strip(),
            "smtp_from_email": str(config.get("smtp_from_email", "") or "").strip(),
            "smtp_use_ssl": str(bool(config.get("smtp_use_ssl", True))).lower(),
            "resend_enabled": str(bool(config.get("resend_enabled", False))).lower(),
            "resend_api_key": str(config.get("resend_api_key", "") or "").strip(),
            "resend_from_email": str(config.get("resend_from_email", "") or "").strip(),
        }

        return await self.update_settings(session, settings_to_update)

    async def get_idc_config(self, session: AsyncSession) -> Dict[str, Any]:
        """获取 IDC 打赏配置"""
        enabled = await self.get_setting(session, "idc_enabled", "false")
        pid = await self.get_setting(session, "idc_pid", "")
        key = await self.get_setting(session, "idc_key", "")
        amount_raw = await self.get_setting(session, "idc_amount", "6.66")

        try:
            amount = str(float(amount_raw))
        except (TypeError, ValueError):
            amount = "6.66"

        return {
            "enabled": (enabled or "false").lower() == "true",
            "pid": (pid or "").strip(),
            "key": (key or "").strip(),
            "amount": amount,
        }

    async def update_idc_config(self, session: AsyncSession, config: Dict[str, Any]) -> bool:
        """更新 IDC 打赏配置"""
        amount = config.get("amount", "6.66")
        try:
            amount = str(float(amount))
        except (TypeError, ValueError):
            amount = "6.66"

        settings_to_update = {
            "idc_enabled": str(bool(config.get("enabled", False))).lower(),
            "idc_pid": str(config.get("pid", "") or "").strip(),
            "idc_key": str(config.get("key", "") or "").strip(),
            "idc_amount": amount,
        }
        return await self.update_settings(session, settings_to_update)

    async def get_linuxdo_oauth_config(self, session: AsyncSession) -> Dict[str, Any]:
        """获取 LinuxDo OAuth 配置"""
        from app.config import settings as app_settings

        enabled = await self.get_setting(session, "linuxdo_oauth_enabled")
        client_id = await self.get_setting(session, "linuxdo_client_id")
        client_secret = await self.get_setting(session, "linuxdo_client_secret")
        authorize_url = await self.get_setting(session, "linuxdo_authorize_url")
        token_url = await self.get_setting(session, "linuxdo_token_url")
        userinfo_url = await self.get_setting(session, "linuxdo_userinfo_url")
        scope = await self.get_setting(session, "linuxdo_scope")
        redirect_path = await self.get_setting(session, "linuxdo_redirect_path")

        return {
            "enabled": (enabled or str(app_settings.linuxdo_oauth_enabled)).lower() == "true",
            "client_id": client_id if client_id is not None else app_settings.linuxdo_client_id,
            "client_secret": client_secret if client_secret is not None else app_settings.linuxdo_client_secret,
            "authorize_url": authorize_url if authorize_url is not None else app_settings.linuxdo_authorize_url,
            "token_url": token_url if token_url is not None else app_settings.linuxdo_token_url,
            "userinfo_url": userinfo_url if userinfo_url is not None else app_settings.linuxdo_userinfo_url,
            "scope": scope if scope is not None else app_settings.linuxdo_scope,
            "redirect_path": redirect_path if redirect_path is not None else app_settings.linuxdo_redirect_path,
        }

    async def update_linuxdo_oauth_config(self, session: AsyncSession, config: Dict[str, Any]) -> bool:
        """更新 LinuxDo OAuth 配置"""
        settings_to_update = {
            "linuxdo_oauth_enabled": str(bool(config.get("enabled", False))).lower(),
            "linuxdo_client_id": str(config.get("client_id", "") or "").strip(),
            "linuxdo_client_secret": str(config.get("client_secret", "") or "").strip(),
            "linuxdo_authorize_url": str(config.get("authorize_url", "") or "").strip(),
            "linuxdo_token_url": str(config.get("token_url", "") or "").strip(),
            "linuxdo_userinfo_url": str(config.get("userinfo_url", "") or "").strip(),
            "linuxdo_scope": str(config.get("scope", "") or "").strip(),
            "linuxdo_redirect_path": str(config.get("redirect_path", "") or "").strip(),
        }
        return await self.update_settings(session, settings_to_update)

    async def get_maintenance_config(self, session: AsyncSession) -> Dict[str, Any]:
        """获取维护模式配置"""
        enabled = await self.get_setting(session, "maintenance_enabled", "false")
        end_time = await self.get_setting(session, "maintenance_end_time", "")
        title = await self.get_setting(session, "maintenance_title", "系统维护中")
        content = await self.get_setting(session, "maintenance_content", "系统正在维护，请稍后再试")
        video_enabled = await self.get_setting(session, "maintenance_video_enabled", "false")
        default_embed = "<iframe src=\"//player.bilibili.com/player.html?isOutside=true&aid=393018479&bvid=BV1ad4y1V7wb&cid=971466390&p=1\" scrolling=\"no\" border=\"0\" frameborder=\"no\" framespacing=\"0\" allowfullscreen=\"true\"></iframe>"
        video_embed = await self.get_setting(session, "maintenance_video_embed", default_embed)

        return {
            "enabled": (enabled or "false").lower() == "true",
            "end_time": (end_time or "").strip(),
            "title": (title or "系统维护中").strip() or "系统维护中",
            "content": (content or "系统正在维护，请稍后再试").strip() or "系统正在维护，请稍后再试",
            "video_enabled": (video_enabled or "false").lower() == "true",
            "video_embed": (video_embed or default_embed).strip(),
        }

    async def update_maintenance_config(self, session: AsyncSession, config: Dict[str, Any]) -> bool:
        """更新维护模式配置"""
        settings_to_update = {
            "maintenance_enabled": str(bool(config.get("enabled", False))).lower(),
            "maintenance_end_time": str(config.get("end_time", "") or "").strip(),
            "maintenance_title": str(config.get("title", "系统维护中") or "系统维护中").strip(),
            "maintenance_content": str(config.get("content", "系统正在维护，请稍后再试") or "系统正在维护，请稍后再试").strip(),
            "maintenance_video_enabled": str(bool(config.get("video_enabled", False))).lower(),
            "maintenance_video_embed": str(config.get("video_embed", "") or "").strip(),
        }
        return await self.update_settings(session, settings_to_update)

    # ===== 公告管理 =====

    async def get_announcement(self, session: AsyncSession) -> dict:
        """
        获取公告内容

        Returns:
            公告字典: {"enabled": bool, "content": str}
        """
        enabled = await self.get_setting(session, "announcement_enabled", "false")
        content = await self.get_setting(session, "announcement_content", "")
        return {
            "enabled": enabled == "true",
            "content": content
        }

    async def update_announcement(self, session: AsyncSession, content: str, enabled: bool = True) -> bool:
        """
        更新公告内容

        Args:
            session: 数据库会话
            content: 公告内容
            enabled: 是否启用

        Returns:
            是否更新成功
        """
        settings_to_update = {
            "announcement_enabled": str(enabled).lower(),
            "announcement_content": content
        }
        success = await self.update_settings(session, settings_to_update)
        if success:
            logger.info(f"公告已更新: enabled={enabled}, content_length={len(content)}")
    # ===== 节日装饰管理 =====

    async def get_festive_config(self, session: AsyncSession) -> Dict[str, Any]:
        """获取节日装饰配置"""
        enabled = await self.get_setting(session, "festive_enabled", "false")
        return {
            "enabled": enabled.lower() == "true",
        }

    async def update_festive_config(self, session: AsyncSession, config: Dict[str, Any]) -> bool:
        """更新节日装饰配置"""
        settings_to_update = {
            "festive_enabled": str(bool(config.get("enabled", False))).lower(),
        }
        return await self.update_settings(session, settings_to_update)


# 创建全局实例
settings_service = SettingsService()
