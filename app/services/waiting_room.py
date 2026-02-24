"""
候车室服务
管理等待免费车位用户的加入、查询和邮件通知
"""
import logging
import httpx
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import WaitingRoom

logger = logging.getLogger(__name__)


class WaitingRoomService:
    """候车室服务类"""

    async def join(self, session: AsyncSession, email: str) -> dict:
        """
        用户加入候车室

        Args:
            session: 数据库会话
            email: 用户邮箱

        Returns:
            {"success": bool, "message": str}
        """
        try:
            # 检查是否已在候车室（未通知的）
            result = await session.execute(
                select(WaitingRoom).where(
                    WaitingRoom.email == email,
                    WaitingRoom.notified == False
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                return {"success": True, "message": "您已在候车室中，有车位时会通知您"}

            # 加入候车室
            entry = WaitingRoom(email=email, notified=False)
            session.add(entry)
            await session.commit()

            logger.info(f"用户 {email} 加入候车室")
            return {"success": True, "message": "已加入候车室，有车位时会通过邮件通知您"}

        except Exception as e:
            logger.error(f"加入候车室失败: {e}")
            await session.rollback()
            return {"success": False, "message": "加入失败，请稍后重试"}

    async def get_waiting_list(self, session: AsyncSession) -> List[dict]:
        """
        获取候车室列表（管理员用）

        Returns:
            候车用户列表
        """
        result = await session.execute(
            select(WaitingRoom).order_by(WaitingRoom.created_at.desc())
        )
        entries = result.scalars().all()

        return [
            {
                "id": e.id,
                "email": e.email,
                "notified": e.notified,
                "is_priority": getattr(e, "is_priority", False) or False,
                "idc_order_no": getattr(e, "idc_order_no", None),
                "created_at": e.created_at.isoformat() if e.created_at else None,
                "notified_at": e.notified_at.isoformat() if e.notified_at else None,
            }
            for e in entries
        ]

    async def get_waiting_count(self, session: AsyncSession) -> int:
        """获取未通知的候车人数"""
        result = await session.execute(
            select(func.count(WaitingRoom.id)).where(WaitingRoom.notified == False)
        )
        return result.scalar() or 0

    async def notify_all(
        self,
        session: AsyncSession,
        resend_api_key: str = "",
        from_email: str = "",
        smtp_config: Optional[dict] = None,
    ) -> dict:
        """
        通知所有未通知的候车用户（有车位了）

        Args:
            session: 数据库会话
            resend_api_key: Resend API Key（可选）
            from_email: Resend 发件人邮箱（可选）
            smtp_config: SMTP 配置字典（可选）

        Returns:
            {"success": bool, "message": str, "notified_count": int}
        """
        try:
            # 获取当前可用的免费车位数
            from app.services.team import TeamService
            team_service = TeamService()
            free_result = await team_service.get_free_spot_teams(session)
            free_teams = free_result.get("teams", [])
            available_spots = sum(
                t.get("available_spots", 0) for t in free_teams
            )

            # 获取所有未通知的用户
            result = await session.execute(
                select(WaitingRoom).where(WaitingRoom.notified == False)
            )
            entries = result.scalars().all()

            if not entries:
                return {"success": True, "message": "没有需要通知的用户", "notified_count": 0}

            notified_count = 0
            now = datetime.utcnow()

            for entry in entries:
                try:
                    sent = await self._send_email(
                        to_email=entry.email,
                        available_spots=available_spots,
                        resend_api_key=resend_api_key,
                        resend_from_email=from_email,
                        smtp_config=smtp_config,
                    )
                    if sent:
                        entry.notified = True
                        entry.notified_at = now
                        notified_count += 1
                        logger.info(f"已通知候车用户: {entry.email}")
                    else:
                        logger.warning(f"通知候车用户失败: {entry.email}")
                except Exception as e:
                    logger.error(f"通知 {entry.email} 异常: {e}")

            await session.commit()

            return {
                "success": True,
                "message": f"已通知 {notified_count}/{len(entries)} 位用户",
                "notified_count": notified_count
            }

        except Exception as e:
            logger.error(f"批量通知失败: {e}")
            await session.rollback()
            return {"success": False, "message": f"通知失败: {str(e)}", "notified_count": 0}

    def _build_html_content(self, available_spots: int, to_email: str = "") -> str:
        """构建通知邮件 HTML 内容（每封邮件包含收件人邮箱，防止被判为垃圾邮件）"""
        site_url = "https://dash.xpzsd.codes"
        free_spot_url = f"{site_url}/free-spot"

        # 邮箱个性化称呼
        greeting = f"<p style=\"margin:0 0 16px;font-size:15px;line-height:1.7;color:#333;\">{to_email} 您好，</p>" if to_email else "<p style=\"margin:0 0 16px;font-size:15px;line-height:1.7;color:#333;\">您好，</p>"

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
            "<h1 style=\"margin:0;font-size:20px;color:#333;font-weight:600;\">GPT Team - 车位通知</h1>"
            "</td></tr>"
            "<tr><td style=\"padding:32px 40px;\">"
            f"{greeting}"
            "<p style=\"margin:0 0 16px;font-size:15px;line-height:1.7;color:#333;\">"
            "您之前登记等待的 ChatGPT Team 免费车位现已开放。</p>"
            f"<p style=\"margin:0 0 16px;font-size:15px;line-height:1.7;color:#333;\">"
            f"本次开放 <strong style=\"color:#2563eb;font-size:18px;\">{available_spots}</strong> 个车位，先到先得。</p>"
            "<p style=\"margin:0 0 24px;font-size:15px;line-height:1.7;color:#333;\">"
            "请尽快前往免费车位页面完成加入，车位数量有限，先到先得。</p>"
            "<table cellpadding=\"0\" cellspacing=\"0\" style=\"margin:0 0 24px;\">"
            "<tr><td align=\"center\" style=\"background:#2563eb;border-radius:6px;\">"
            f"<a href=\"{free_spot_url}\" target=\"_blank\" style=\"display:inline-block;padding:12px 32px;"
            "font-size:15px;font-weight:600;color:#ffffff;text-decoration:none;\">"
            "立即前往免费车位</a>"
            "</td></tr></table>"
            "<p style=\"margin:0;font-size:13px;color:#999;line-height:1.6;\">"
            "如果您已不需要，请忽略此邮件。</p>"
            "</td></tr>"
            "<tr><td style=\"padding:20px 40px;border-top:1px solid #f0f0f0;\">"
            "<p style=\"margin:0;font-size:12px;color:#aaa;line-height:1.5;\">此邮件由系统自动发送，请勿直接回复。</p>"
            "</td></tr>"
            "</table></td></tr></table></body></html>"
        )

    async def _send_via_resend(self, api_key: str, from_email: str, to_email: str, html_content: str) -> bool:
        """通过 Resend API 发送邮件"""
        try:
            from_field = from_email
            if "<" not in from_email:
                from_field = f"GPT Team <{from_email}>"

            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": from_field,
                        "to": [to_email],
                        "subject": "ChatGPT Team 免费车位已开放",
                        "html": html_content
                    }
                )
                if resp.status_code in (200, 201):
                    logger.info(f"[Resend] 邮件发送成功: {to_email}")
                    return True
                else:
                    logger.error(f"[Resend] 邮件发送失败: {to_email}, status={resp.status_code}, body={resp.text}")
                    return False
        except Exception as e:
            logger.error(f"[Resend] 邮件发送异常: {to_email}, error={e}")
            return False

    def _send_via_smtp_sync(self, smtp_config: dict, to_email: str, html_content: str) -> bool:
        """通过 SMTP 发送邮件（同步，支持 Gmail / QQ 邮箱）"""
        try:
            host = smtp_config["host"]
            port = smtp_config["port"]
            username = smtp_config["username"]
            password = smtp_config["password"]
            from_email = smtp_config.get("from_email") or username
            use_ssl = smtp_config.get("use_ssl", True)

            msg = MIMEMultipart("alternative")
            msg["Subject"] = "ChatGPT Team 免费车位已开放"
            msg["From"] = f"GPT Team <{from_email}>"
            msg["To"] = to_email

            msg.attach(MIMEText(html_content, "html", "utf-8"))

            if use_ssl:
                # SSL 直连（QQ 邮箱 465 端口）
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(host, port, context=context, timeout=15) as server:
                    server.login(username, password)
                    server.sendmail(from_email, [to_email], msg.as_string())
            else:
                # STARTTLS（Gmail 587 端口）
                with smtplib.SMTP(host, port, timeout=15) as server:
                    server.ehlo()
                    server.starttls(context=ssl.create_default_context())
                    server.ehlo()
                    server.login(username, password)
                    server.sendmail(from_email, [to_email], msg.as_string())

            logger.info(f"[SMTP] 邮件发送成功: {to_email} (via {host})")
            return True
        except Exception as e:
            logger.error(f"[SMTP] 邮件发送异常: {to_email}, error={e}")
            return False

    async def _send_via_smtp(self, smtp_config: dict, to_email: str, html_content: str) -> bool:
        """异步包装 SMTP 发送（在线程池中执行同步 SMTP）"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._send_via_smtp_sync, smtp_config, to_email, html_content
        )

    async def _send_email(
        self,
        to_email: str,
        available_spots: int = 0,
        resend_api_key: str = "",
        resend_from_email: str = "",
        smtp_config: Optional[dict] = None,
    ) -> bool:
        """
        统一发送邮件入口：优先使用 SMTP，若未配置则使用 Resend

        Args:
            to_email: 收件人邮箱
            available_spots: 当前可用车位数
            resend_api_key: Resend API Key
            resend_from_email: Resend 发件人邮箱
            smtp_config: SMTP 配置字典

        Returns:
            是否发送成功
        """
        html_content = self._build_html_content(available_spots, to_email)

        # 优先使用 SMTP
        if smtp_config and smtp_config.get("enabled") and smtp_config.get("host"):
            return await self._send_via_smtp(smtp_config, to_email, html_content)

        # 回退到 Resend
        if resend_api_key:
            return await self._send_via_resend(resend_api_key, resend_from_email, to_email, html_content)

        logger.error(f"未配置任何邮件发送方式，无法发送邮件给: {to_email}")
        return False

    async def notify_priority(
        self,
        session: AsyncSession,
        resend_api_key: str = "",
        from_email: str = "",
        smtp_config: Optional[dict] = None,
    ) -> dict:
        """
        仅通知优先用户（已打赏 IDC 的用户）

        Args:
            session: 数据库会话
            resend_api_key: Resend API Key（可选）
            from_email: Resend 发件人邮箱（可选）
            smtp_config: SMTP 配置字典（可选）

        Returns:
            {"success": bool, "message": str, "notified_count": int}
        """
        try:
            from app.services.team import TeamService
            team_service = TeamService()
            free_result = await team_service.get_free_spot_teams(session)
            free_teams = free_result.get("teams", [])
            available_spots = sum(
                t.get("available_spots", 0) for t in free_teams
            )

            result = await session.execute(
                select(WaitingRoom).where(
                    WaitingRoom.notified == False,
                    WaitingRoom.is_priority == True
                )
            )
            entries = result.scalars().all()

            if not entries:
                return {"success": True, "message": "没有需要通知的优先用户", "notified_count": 0}

            notified_count = 0
            now = datetime.utcnow()

            for entry in entries:
                try:
                    sent = await self._send_email(
                        to_email=entry.email,
                        available_spots=available_spots,
                        resend_api_key=resend_api_key,
                        resend_from_email=from_email,
                        smtp_config=smtp_config,
                    )
                    if sent:
                        entry.notified = True
                        entry.notified_at = now
                        notified_count += 1
                        logger.info(f"已通知优先用户: {entry.email}")
                    else:
                        logger.warning(f"通知优先用户失败: {entry.email}")
                except Exception as e:
                    logger.error(f"通知 {entry.email} 异常: {e}")

            await session.commit()

            return {
                "success": True,
                "message": f"已通知 {notified_count}/{len(entries)} 位优先用户",
                "notified_count": notified_count
            }

        except Exception as e:
            logger.error(f"通知优先用户失败: {e}")
            await session.rollback()
            return {"success": False, "message": f"通知失败: {str(e)}", "notified_count": 0}

    async def delete_entry(self, session: AsyncSession, entry_id: int) -> bool:
        """删除单个候车记录"""
        try:
            result = await session.execute(
                select(WaitingRoom).where(WaitingRoom.id == entry_id)
            )
            entry = result.scalar_one_or_none()
            if not entry:
                return False
            await session.delete(entry)
            await session.commit()
            logger.info(f"已删除候车记录: id={entry_id}, email={entry.email}")
            return True
        except Exception as e:
            logger.error(f"删除候车记录失败: {e}")
            await session.rollback()
            return False

    async def clear_notified(self, session: AsyncSession) -> bool:
        """清除已通知的记录"""
        try:
            result = await session.execute(
                select(WaitingRoom).where(WaitingRoom.notified == True)
            )
            entries = result.scalars().all()
            for e in entries:
                await session.delete(e)
            await session.commit()
            logger.info(f"已清除 {len(entries)} 条已通知记录")
            return True
        except Exception as e:
            logger.error(f"清除已通知记录失败: {e}")
            await session.rollback()
            return False


# 全局实例
waiting_room_service = WaitingRoomService()
