"""
兑换流程服务
协调用户兑换流程，包括验证、Team选择、邀请发送、事务处理和并发控制
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Team, RedemptionCode, RedemptionRecord
from app.services.redemption import RedemptionService
from app.services.team import TeamService
from app.services.chatgpt import ChatGPTService
from app.services.encryption import encryption_service

logger = logging.getLogger(__name__)


class RedeemFlowService:
    """兑换流程服务类"""

    def __init__(self):
        """初始化兑换流程服务"""
        self.redemption_service = RedemptionService()
        self.team_service = TeamService()
        self.chatgpt_service = ChatGPTService()

    async def verify_code_and_get_teams(
        self,
        code: str,
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """
        验证兑换码并获取可用 Team 列表

        Args:
            code: 兑换码
            db_session: 数据库会话

        Returns:
            结果字典,包含 success, valid, reason, teams, error
        """
        try:
            # 1. 验证兑换码
            validate_result = await self.redemption_service.validate_code(code, db_session)

            if not validate_result["success"]:
                return {
                    "success": False,
                    "valid": False,
                    "reason": None,
                    "teams": [],
                    "error": validate_result["error"]
                }

            if not validate_result["valid"]:
                return {
                    "success": True,
                    "valid": False,
                    "reason": validate_result["reason"],
                    "teams": [],
                    "error": None
                }

            # 2. 获取可用 Team 列表
            teams_result = await self.team_service.get_available_teams(db_session)

            if not teams_result["success"]:
                return {
                    "success": False,
                    "valid": True,
                    "reason": None,
                    "teams": [],
                    "error": teams_result["error"]
                }

            logger.info(f"验证兑换码成功: {code}, 可用 Team 数量: {len(teams_result['teams'])}")

            return {
                "success": True,
                "valid": True,
                "reason": None,
                "teams": teams_result["teams"],
                "error": None
            }

        except Exception as e:
            logger.error(f"验证兑换码并获取 Team 列表失败: {e}")
            return {
                "success": False,
                "valid": False,
                "reason": None,
                "teams": [],
                "error": f"验证失败: {str(e)}"
            }

    async def select_team_auto(
        self,
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """
        自动选择 Team (选择过期时间最早的)

        Args:
            db_session: 数据库会话

        Returns:
            结果字典,包含 success, team_id, error
        """
        try:
            # 查询可用 Team，按过期时间升序排序（排除免费车位 Team）
            stmt = select(Team).where(
                Team.status == "active",
                Team.current_members < Team.max_members,
                Team.is_free_spot == False
            ).order_by(Team.expires_at.asc()).limit(1)

            result = await db_session.execute(stmt)
            team = result.scalar_one_or_none()

            if not team:
                return {
                    "success": False,
                    "team_id": None,
                    "error": "没有可用的 Team"
                }

            logger.info(f"自动选择 Team: {team.id} (过期时间: {team.expires_at})")

            return {
                "success": True,
                "team_id": team.id,
                "error": None
            }

        except Exception as e:
            logger.error(f"自动选择 Team 失败: {e}")
            return {
                "success": False,
                "team_id": None,
                "error": f"自动选择 Team 失败: {str(e)}"
            }

    async def redeem_and_join_team(
        self,
        email: str,
        code: str,
        team_id: Optional[int],
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """
        完整的兑换流程 (带事务和并发控制)

        Args:
            email: 用户邮箱
            code: 兑换码
            team_id: Team ID (如果为 None 则自动选择)
            db_session: 数据库会话

        Returns:
            结果字典,包含 success, message, team_info, error
        """
        try:
            # 开启事务
            async with db_session.begin_nested():
                # 1. 验证兑换码
                validate_result = await self.redemption_service.validate_code(code, db_session)

                if not validate_result["success"]:
                    return {
                        "success": False,
                        "message": None,
                        "team_info": None,
                        "error": validate_result["error"]
                    }

                if not validate_result["valid"]:
                    return {
                        "success": False,
                        "message": None,
                        "team_info": None,
                        "error": validate_result["reason"]
                    }

                # 2. 选择 Team (如果未指定则自动选择)
                # Test-only redemption code: trigger success animation without real invite.
                if code.upper().startswith("TEST-"):
                    logger.info(f"Test redemption code used: {code} -> {email}")
                    return {
                        "success": True,
                        "message": "测试兑换成功（仅演示动画，未发送真实邀请）",
                        "team_info": {
                            "team_id": 0,
                            "team_name": "动画测试模式",
                            "account_id": "TEST-MODE",
                            "expires_at": None
                        },
                        "error": None,
                        "is_test_mode": True
                    }

                if team_id is None:
                    select_result = await self.select_team_auto(db_session)
                    if not select_result["success"]:
                        return {
                            "success": False,
                            "message": None,
                            "team_info": None,
                            "error": select_result["error"]
                        }
                    team_id = select_result["team_id"]

                # 3. 锁定 Team 行 (FOR UPDATE)
                stmt = select(Team).where(Team.id == team_id).with_for_update()
                result = await db_session.execute(stmt)
                team = result.scalar_one_or_none()

                if not team:
                    return {
                        "success": False,
                        "message": None,
                        "team_info": None,
                        "error": f"Team ID {team_id} 不存在"
                    }

                # 4. 检查是否为免费车位 Team（不允许兑换码上车）
                if team.is_free_spot:
                    return {
                        "success": False,
                        "message": None,
                        "team_info": None,
                        "error": "该 Team 为免费车位，不能使用兑换码上车"
                    }

                # 5. 再次检查 Team 容量 (防止并发冲突)
                if team.current_members >= team.max_members:
                    return {
                        "success": False,
                        "message": None,
                        "team_info": None,
                        "error": "Team 已满，请选择其他 Team"
                    }

                if team.status != "active":
                    return {
                        "success": False,
                        "message": None,
                        "team_info": None,
                        "error": f"Team 状态异常: {team.status}"
                    }

                # 5. 解密 AT Token
                try:
                    access_token = encryption_service.decrypt_token(team.access_token_encrypted)
                except Exception as e:
                    logger.error(f"解密 Token 失败: {e}")
                    return {
                        "success": False,
                        "message": None,
                        "team_info": None,
                        "error": f"解密 Token 失败: {str(e)}"
                    }

                # 6. 调用 ChatGPT API 发送邀请
                invite_result = await self.chatgpt_service.send_invite(
                    access_token,
                    team.account_id,
                    email,
                    db_session
                )

                if not invite_result["success"]:
                    # API 调用失败，回滚事务
                    return {
                        "success": False,
                        "message": None,
                        "team_info": None,
                        "error": f"发送邀请失败: {invite_result['error']}"
                    }

                # 7. 更新兑换码状态
                stmt = select(RedemptionCode).where(RedemptionCode.code == code)
                result = await db_session.execute(stmt)
                redemption_code = result.scalar_one_or_none()

                redemption_code.status = "used"
                redemption_code.used_by_email = email
                redemption_code.used_team_id = team_id
                redemption_code.used_at = datetime.now()

                # 8. 创建使用记录
                redemption_record = RedemptionRecord(
                    email=email,
                    code=code,
                    team_id=team_id,
                    account_id=team.account_id
                )
                db_session.add(redemption_record)

                # 9. 更新 Team 成员数
                team.current_members += 1

                # 更新状态
                if team.current_members >= team.max_members:
                    team.status = "full"

                # 提交嵌套事务
                await db_session.commit()

                logger.info(f"兑换成功: {email} 加入 Team {team_id} (兑换码: {code})")

                return {
                    "success": True,
                    "message": f"成功加入 Team: {team.team_name}",
                    "team_info": {
                        "team_id": team.id,
                        "team_name": team.team_name,
                        "account_id": team.account_id,
                        "expires_at": team.expires_at.isoformat() if team.expires_at else None
                    },
                    "error": None
                }

        except Exception as e:
            await db_session.rollback()
            logger.error(f"兑换流程失败: {e}")
            return {
                "success": False,
                "message": None,
                "team_info": None,
                "error": f"兑换失败: {str(e)}"
            }

    # ==================== 质保功能 ====================

    async def _get_warranty_days(self, db_session: AsyncSession, redemption_code=None) -> int:
        """获取质保天数：优先用兑换码自身设置，否则用全局默认"""
        if redemption_code and redemption_code.warranty_days:
            return redemption_code.warranty_days
        from app.services.settings import settings_service
        return await settings_service.get_warranty_days(db_session)

    async def warranty_query(
        self,
        code: str,
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """
        质保查询：检查兑换码是否支持质保重新兑换

        Returns:
            包含质保状态信息的字典
        """
        try:
            stmt = select(RedemptionCode).where(RedemptionCode.code == code)
            result = await db_session.execute(stmt)
            redemption_code = result.scalar_one_or_none()

            if not redemption_code:
                return {"success": False, "error": "兑换码不存在"}

            if not redemption_code.is_warranty:
                return {"success": False, "error": "该兑换码不是质保兑换码，不支持质保服务"}

            if redemption_code.status == "unused":
                return {"success": False, "error": "该兑换码尚未使用，无需质保"}

            if redemption_code.status == "expired":
                return {"success": False, "error": "该兑换码已过期"}

            # 检查质保期
            if not redemption_code.used_at:
                return {"success": False, "error": "无法确认使用时间，请联系管理员"}

            warranty_days = await self._get_warranty_days(db_session, redemption_code)
            warranty_deadline = redemption_code.used_at + timedelta(days=warranty_days)
            now = datetime.now()

            if now > warranty_deadline:
                return {
                    "success": False,
                    "error": f"质保已过期（使用时间: {redemption_code.used_at.strftime('%Y-%m-%d')}，"
                             f"质保截止: {warranty_deadline.strftime('%Y-%m-%d')}）"
                }

            remaining_days = (warranty_deadline - now).days

            # 查询使用记录
            stmt = select(RedemptionRecord).where(
                RedemptionRecord.code == code
            ).order_by(RedemptionRecord.redeemed_at.desc())
            result = await db_session.execute(stmt)
            records = result.scalars().all()

            return {
                "success": True,
                "warranty_info": {
                    "code": code,
                    "is_warranty": True,
                    "status": redemption_code.status,
                    "used_by_email": redemption_code.used_by_email,
                    "used_at": redemption_code.used_at.strftime("%Y-%m-%d %H:%M"),
                    "warranty_deadline": warranty_deadline.strftime("%Y-%m-%d"),
                    "remaining_days": remaining_days,
                    "warranty_days": warranty_days,
                    "warranty_redeem_count": redemption_code.warranty_count or 0,
                    "can_warranty_redeem": True,
                    "records": [
                        {
                            "email": r.email,
                            "team_id": r.team_id,
                            "redeemed_at": r.redeemed_at.strftime("%Y-%m-%d %H:%M") if r.redeemed_at else None,
                            "is_warranty_redeem": r.is_warranty_redeem
                        }
                        for r in records
                    ]
                }
            }

        except Exception as e:
            logger.error(f"质保查询失败: {e}")
            return {"success": False, "error": f"查询失败: {str(e)}"}

    async def warranty_redeem(
        self,
        email: str,
        code: str,
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """
        质保重新兑换：封号后使用原质保兑换码重新加入 Team
        """
        try:
            async with db_session.begin_nested():
                # 1. 查询兑换码
                stmt = select(RedemptionCode).where(RedemptionCode.code == code)
                result = await db_session.execute(stmt)
                redemption_code = result.scalar_one_or_none()

                if not redemption_code:
                    return {"success": False, "message": None, "team_info": None,
                            "error": "兑换码不存在"}

                if not redemption_code.is_warranty:
                    return {"success": False, "message": None, "team_info": None,
                            "error": "该兑换码不是质保兑换码，不支持质保重新兑换"}

                if redemption_code.status != "used":
                    return {"success": False, "message": None, "team_info": None,
                            "error": f"兑换码状态异常: {redemption_code.status}，无法进行质保兑换"}

                # 2. 检查质保期
                if not redemption_code.used_at:
                    return {"success": False, "message": None, "team_info": None,
                            "error": "无法确认使用时间，请联系管理员"}

                warranty_days = await self._get_warranty_days(db_session, redemption_code)
                warranty_deadline = redemption_code.used_at + timedelta(days=warranty_days)
                if datetime.now() > warranty_deadline:
                    return {"success": False, "message": None, "team_info": None,
                            "error": f"质保已过期（质保截止: {warranty_deadline.strftime('%Y-%m-%d')}）"}

                # 3. 自动选择 Team
                select_result = await self.select_team_auto(db_session)
                if not select_result["success"]:
                    return {"success": False, "message": None, "team_info": None,
                            "error": select_result["error"]}
                team_id = select_result["team_id"]

                # 4. 锁定 Team
                stmt = select(Team).where(Team.id == team_id).with_for_update()
                result = await db_session.execute(stmt)
                team = result.scalar_one_or_none()

                if not team:
                    return {"success": False, "message": None, "team_info": None,
                            "error": f"Team ID {team_id} 不存在"}

                if team.current_members >= team.max_members:
                    return {"success": False, "message": None, "team_info": None,
                            "error": "Team 已满，请联系管理员"}

                if team.status != "active":
                    return {"success": False, "message": None, "team_info": None,
                            "error": f"Team 状态异常: {team.status}"}

                # 5. 解密 Token
                try:
                    access_token = encryption_service.decrypt_token(team.access_token_encrypted)
                except Exception as e:
                    logger.error(f"解密 Token 失败: {e}")
                    return {"success": False, "message": None, "team_info": None,
                            "error": f"解密 Token 失败: {str(e)}"}

                # 6. 发送邀请
                invite_result = await self.chatgpt_service.send_invite(
                    access_token, team.account_id, email, db_session
                )
                if not invite_result["success"]:
                    return {"success": False, "message": None, "team_info": None,
                            "error": f"发送邀请失败: {invite_result['error']}"}

                # 7. 更新兑换码质保计数
                redemption_code.warranty_count = (redemption_code.warranty_count or 0) + 1

                # 8. 创建使用记录（标记为质保兑换）
                warranty_record = RedemptionRecord(
                    email=email,
                    code=code,
                    team_id=team_id,
                    account_id=team.account_id,
                    is_warranty_redeem=True
                )
                db_session.add(warranty_record)

                # 9. 更新 Team 成员数
                team.current_members += 1
                if team.current_members >= team.max_members:
                    team.status = "full"

                await db_session.commit()

                logger.info(f"质保兑换成功: {email} 使用 {code} 加入 Team {team_id} (第{redemption_code.warranty_count}次质保)")

                return {
                    "success": True,
                    "message": f"质保兑换成功！已重新加入 Team: {team.team_name}",
                    "team_info": {
                        "team_id": team.id,
                        "team_name": team.team_name,
                        "account_id": team.account_id,
                        "expires_at": team.expires_at.isoformat() if team.expires_at else None
                    },
                    "warranty_count": redemption_code.warranty_count,
                    "error": None
                }

        except Exception as e:
            await db_session.rollback()
            logger.error(f"质保兑换失败: {e}")
            return {"success": False, "message": None, "team_info": None,
                    "error": f"质保兑换失败: {str(e)}"}


    async def free_spot_join(
        self,
        email: str,
        team_id: int,
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """
        免费车位加入：无需兑换码，直接加入指定的免费车位 Team
        """
        try:
            async with db_session.begin_nested():
                # 1. 锁定 Team 行
                stmt = select(Team).where(Team.id == team_id).with_for_update()
                result = await db_session.execute(stmt)
                team = result.scalar_one_or_none()

                if not team:
                    return {"success": False, "message": None, "error": f"Team ID {team_id} 不存在"}

                if not team.is_free_spot:
                    return {"success": False, "message": None, "error": "该 Team 不是免费车位"}

                if team.is_exclusive:
                    return {"success": False, "message": None, "error": "该车位为打赏用户专属，请使用专属链接上车"}

                if team.status != "active":
                    return {"success": False, "message": None, "error": f"Team 状态异常: {team.status}"}

                if team.current_members >= team.max_members:
                    return {"success": False, "message": None, "error": "该车位已满"}

                # 2. 解密 Token
                try:
                    access_token = encryption_service.decrypt_token(team.access_token_encrypted)
                except Exception as e:
                    logger.error(f"解密 Token 失败: {e}")
                    return {"success": False, "message": None, "error": f"解密 Token 失败: {str(e)}"}

                # 3. 发送邀请
                invite_result = await self.chatgpt_service.send_invite(
                    access_token, team.account_id, email, db_session
                )
                if not invite_result["success"]:
                    return {"success": False, "message": None,
                            "error": f"发送邀请失败: {invite_result['error']}"}

                # 4. 更新成员数
                team.current_members += 1
                if team.current_members >= team.max_members:
                    team.status = "full"

                await db_session.commit()

                logger.info(f"免费车位加入成功: {email} -> Team {team_id}")

                return {
                    "success": True,
                    "message": f"成功加入 Team: {team.team_name}，请查收邮箱邀请",
                    "team_info": {
                        "team_id": team.id,
                        "team_name": team.team_name,
                        "account_id": team.account_id,
                        "expires_at": team.expires_at.isoformat() if team.expires_at else None
                    },
                    "error": None
                }

        except Exception as e:
            await db_session.rollback()
            logger.error(f"免费车位加入失败: {e}")
            return {"success": False, "message": None, "error": f"加入失败: {str(e)}"}


# 创建全局实例
redeem_flow_service = RedeemFlowService()
