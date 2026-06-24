from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Enum, DECIMAL, SmallInteger, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

import enum

class UserRole(enum.Enum):
    user = "user"
    shop = "shop"
    admin = "admin"

class SysUser(Base):
    __tablename__ = 'sys_user'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    is_active = Column(SmallInteger, default=1, nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Shop(Base):
    __tablename__ = 'shop'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    owner_id = Column(BigInteger, ForeignKey('sys_user.id'), nullable=False)
    shop_name = Column(String(100), nullable=False)
    cover_image = Column(String(500), nullable=False)
    address = Column(String(200), nullable=False)
    avg_cost = Column(DECIMAL(10,2), nullable=False)
    description = Column(Text)
    good_rate = Column(DECIMAL(5,2), default=0.00, nullable=False)
    is_recommended = Column(SmallInteger, default=0, nullable=False)
    is_active = Column(SmallInteger, default=1, nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ShopProduct(Base):
    __tablename__ = 'shop_product'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    shop_id = Column(BigInteger, ForeignKey('shop.id'), nullable=False)
    product_name = Column(String(100), nullable=False)
    price = Column(DECIMAL(10,2), nullable=False)
    product_image = Column(String(500))
    description = Column(String(500))
    sort = Column(Integer, default=0, nullable=False)
    is_active = Column(SmallInteger, default=1, nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow, nullable=False)

class EvaluationLevel(enum.Enum):
    recommend = 'recommend'
    general = 'general'
    bad = 'bad'

class UserEvaluation(Base):
    __tablename__ = 'user_evaluation'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('sys_user.id'), nullable=False)
    shop_id = Column(BigInteger, ForeignKey('shop.id'), nullable=False)
    level = Column(Enum(EvaluationLevel), nullable=False)
    tags = Column(String(100), nullable=False)
    target_platform = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)
    is_ai_generated = Column(SmallInteger, default=1, nullable=False)
    like_count = Column(Integer, default=0, nullable=False)
    reply_count = Column(Integer, default=0, nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EvaluationReply(Base):
    __tablename__ = 'evaluation_reply'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    evaluation_id = Column(BigInteger, ForeignKey('user_evaluation.id'), nullable=False)
    reply_user_id = Column(BigInteger, ForeignKey('sys_user.id'), nullable=False)
    reply_role = Column(String(16), nullable=False)
    content = Column(Text, nullable=False)
    parent_reply_id = Column(BigInteger, nullable=True, default=None)
    create_time = Column(DateTime, default=datetime.utcnow, nullable=False)

class EvaluationLike(Base):
    __tablename__ = 'evaluation_like'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    evaluation_id = Column(BigInteger, ForeignKey('user_evaluation.id'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('sys_user.id'), nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow, nullable=False)

class UserCollection(Base):
    __tablename__ = 'user_collection'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('sys_user.id'), nullable=False)
    shop_id = Column(BigInteger, ForeignKey('shop.id'), nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow, nullable=False)

class UserBrowseHistory(Base):
    __tablename__ = 'user_browse_history'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('sys_user.id'), nullable=False)
    shop_id = Column(BigInteger, ForeignKey('shop.id'), nullable=False)
    browse_time = Column(DateTime, default=datetime.utcnow, nullable=False)

class SystemConfig(Base):
    __tablename__ = 'system_config'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    config_key = Column(String(50), unique=True, nullable=False)
    config_value = Column(Text)
    remark = Column(String(200))
