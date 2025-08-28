from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.database import Base

class Field(Base):
    __tablename__ = "fields"
    
    id = Column(Integer, primary_key=True, index=True)
    field_name = Column(String(128), unique=True, nullable=False, index=True)  # 字段名
    normalized_name = Column(String(128), unique=True, nullable=False, index=True)  # 规范化名，用于唯一索引
    meaning = Column(Text, nullable=False)  # 业务含义
    data_type = Column(String(20), nullable=False)  # 数据类型：INT、VARCHAR、DATETIME、DECIMAL等
    root_list = Column(Text, nullable=False)  # 使用的词根列表，JSON格式存储
    remark = Column(Text, nullable=True)  # 备注说明
    status = Column(String(20), default="active", nullable=False)  # 状态：active/deprecated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 