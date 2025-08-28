from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.database import Base

class Root(Base):
    __tablename__ = "roots"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False, index=True)  # 词根名
    normalized_name = Column(String(64), unique=True, nullable=False, index=True)  # 规范化名，用于唯一索引
    aliases = Column(Text, nullable=True)  # 别名列表，JSON格式存储
    tags = Column(Text, nullable=True)  # 标签列表，JSON格式存储
    usage_count = Column(Integer, default=0, nullable=False)  # 使用次数
    remark = Column(Text, nullable=True)  # 备注说明
    status = Column(String(20), default="active", nullable=False)  # 状态：active/deprecated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 