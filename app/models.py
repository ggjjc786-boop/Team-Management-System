"""
数据库模型定义
定义所有数据库表的 SQLAlchemy 模型
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Team(Base):
    """Team 信息表"""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, comment="Team 管理员邮箱")
    access_token_encrypted = Column(Text, nullable=False, comment="加密存储的 AT")
    encryption_key_id = Column(String(50), comment="加密密钥 ID")
    account_id = Column(String(100), comment="当前使用的 account-id")
    team_name = Column(String(255), comment="Team 名称")
    plan_type = Column(String(50), comment="计划类型")
    subscription_plan = Column(String(100), comment="订阅计划")
    expires_at = Column(DateTime, comment="订阅到期时间")
    current_members = Column(Integer, default=0, comment="当前成员数")
    max_members = Column(Integer, default=6, comment="最大成员数")
    status = Column(String(20), default="active", comment="状态: active/full/expired/error")
    is_free_spot = Column(Boolean, default=False, comment="是否为免费车位")
    is_exclusive = Column(Boolean, default=False, comment="是否为打赏用户专属")
    last_sync = Column(DateTime, comment="最后同步时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    team_accounts = relationship("TeamAccount", back_populates="team", cascade="all, delete-orphan")
    redemption_records = relationship("RedemptionRecord", back_populates="team")

    # 索引
    __table_args__ = (
        Index("idx_status", "status"),
    )


class TeamAccount(Base):
    """Team Account 关联表"""
    __tablename__ = "team_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(String(100), nullable=False, comment="Account ID")
    account_name = Column(String(255), comment="Account 名称")
    is_primary = Column(Boolean, default=False, comment="是否为主 Account")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    team = relationship("Team", back_populates="team_accounts")

    # 唯一约束
    __table_args__ = (
        Index("idx_team_account", "team_id", "account_id", unique=True),
    )


class RedemptionCode(Base):
    """兑换码表"""
    __tablename__ = "redemption_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(32), unique=True, nullable=False, comment="兑换码")
    status = Column(String(20), default="unused", comment="状态: unused/used/expired")
    is_warranty = Column(Boolean, default=False, comment="是否为质保兑换码")
    warranty_days = Column(Integer, comment="质保天数（仅质保码有效，空则用全局默认）")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    expires_at = Column(DateTime, comment="过期时间")
    used_by_email = Column(String(255), comment="使用者邮箱")
    used_team_id = Column(Integer, ForeignKey("teams.id"), comment="使用的 Team ID")
    used_at = Column(DateTime, comment="使用时间")
    warranty_count = Column(Integer, default=0, comment="质保重新兑换次数")
    is_shop_sold = Column(Boolean, default=False, comment="是否已在积分商城售出")
    shop_sold_to_user_id = Column(Integer, ForeignKey("linuxdo_users.id"), comment="积分商城购买用户 ID")
    shop_sold_at = Column(DateTime, comment="积分商城售出时间")

    # 关系
    redemption_records = relationship("RedemptionRecord", back_populates="redemption_code")

    # 索引
    __table_args__ = (
        Index("idx_code_status", "code", "status"),
    )


class RedemptionRecord(Base):
    """使用记录表"""
    __tablename__ = "redemption_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, comment="用户邮箱")
    code = Column(String(32), ForeignKey("redemption_codes.code"), nullable=False, comment="兑换码")
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, comment="Team ID")
    account_id = Column(String(100), nullable=False, comment="Account ID")
    is_warranty_redeem = Column(Boolean, default=False, comment="是否为质保重新兑换")
    redeemed_at = Column(DateTime, server_default=func.now(), comment="兑换时间")

    # 关系
    team = relationship("Team", back_populates="redemption_records")
    redemption_code = relationship("RedemptionCode", back_populates="redemption_records")

    # 索引
    __table_args__ = (
        Index("idx_email", "email"),
    )


class WaitingRoom(Base):
    """候车室表 - 等待免费车位的用户"""
    __tablename__ = "waiting_room"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, comment="用户邮箱")
    notified = Column(Boolean, default=False, comment="是否已通知")
    is_priority = Column(Boolean, default=False, comment="是否为优先用户(已打赏IDC)")
    idc_order_no = Column(String(64), comment="关联的IDC订单号")
    created_at = Column(DateTime, server_default=func.now(), comment="加入时间")
    notified_at = Column(DateTime, comment="通知时间")

    __table_args__ = (
        Index("idx_waiting_email", "email"),
        Index("idx_waiting_notified", "notified"),
    )


class IdcOrder(Base):
    """IDC 打赏订单表"""
    __tablename__ = "idc_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    out_trade_no = Column(String(64), unique=True, nullable=False, comment="业务订单号")
    trade_no = Column(String(64), comment="平台订单号")
    email = Column(String(255), nullable=False, comment="用户邮箱")
    amount = Column(String(20), nullable=False, comment="打赏金额(IDC)")
    status = Column(String(20), default="pending", comment="状态: pending/paid/expired")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    paid_at = Column(DateTime, comment="支付时间")

    __table_args__ = (
        Index("idx_idc_order_no", "out_trade_no"),
        Index("idx_idc_email", "email"),
    )


class ExclusiveInvite(Base):
    """打赏用户专属邀请链接表"""
    __tablename__ = "exclusive_invites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(64), unique=True, nullable=False, comment="邀请令牌")
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, comment="关联的 Team ID")
    email = Column(String(255), nullable=False, comment="受邀用户邮箱")
    used = Column(Boolean, default=False, comment="是否已使用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    expires_at = Column(DateTime, nullable=False, comment="过期时间")
    used_at = Column(DateTime, comment="使用时间")

    team = relationship("Team")

    __table_args__ = (
        Index("idx_exclusive_token", "token"),
        Index("idx_exclusive_email", "email"),
    )


class Setting(Base):
    """系统设置表"""
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, comment="配置项名称")
    value = Column(Text, comment="配置项值")
    description = Column(String(255), comment="配置项描述")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 索引
    __table_args__ = (
        Index("idx_key", "key"),
    )


class LinuxDoUser(Base):
    """LinuxDo OAuth 用户表"""
    __tablename__ = "linuxdo_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    linuxdo_user_id = Column(String(64), unique=True, nullable=False, comment="LinuxDo 用户唯一 ID")
    username = Column(String(100), nullable=False, comment="LinuxDo 用户名")
    display_name = Column(String(255), comment="显示名称")
    email = Column(String(255), comment="邮箱")
    avatar_url = Column(Text, comment="头像地址")
    points = Column(Integer, default=0, nullable=False, comment="当前积分")
    last_sign_in_at = Column(DateTime, comment="最后签到时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    point_transactions = relationship("PointTransaction", back_populates="user", cascade="all, delete-orphan")
    shop_orders = relationship("ShopOrder", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_linuxdo_user", "linuxdo_user_id"),
        Index("idx_linuxdo_username", "username"),
    )


class PointTransaction(Base):
    """积分流水表"""
    __tablename__ = "point_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("linuxdo_users.id", ondelete="CASCADE"), nullable=False)
    change = Column(Integer, nullable=False, comment="积分变动，正数增加负数扣减")
    type = Column(String(32), nullable=False, comment="变动类型: signin/purchase/adjust")
    description = Column(String(255), comment="变动说明")
    related_order_no = Column(String(64), comment="关联商城订单号")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    user = relationship("LinuxDoUser", back_populates="point_transactions")

    __table_args__ = (
        Index("idx_points_user", "user_id"),
        Index("idx_points_type", "type"),
    )


class ShopOrder(Base):
    """积分商城订单表"""
    __tablename__ = "shop_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(64), unique=True, nullable=False, comment="订单号")
    user_id = Column(Integer, ForeignKey("linuxdo_users.id", ondelete="CASCADE"), nullable=False)
    item_key = Column(String(64), nullable=False, comment="商品标识")
    points_cost = Column(Integer, nullable=False, comment="消耗积分")
    redemption_code_id = Column(Integer, ForeignKey("redemption_codes.id"), comment="发放兑换码 ID")
    redemption_code = Column(String(32), comment="发放兑换码")
    status = Column(String(20), default="success", comment="状态: success/failed")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    user = relationship("LinuxDoUser", back_populates="shop_orders")

    __table_args__ = (
        Index("idx_shop_order_no", "order_no"),
        Index("idx_shop_user", "user_id"),
    )
