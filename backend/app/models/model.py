from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class Model(Base):
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(128), unique=True, nullable=False, index=True)  # 模型名
    description = Column(Text, nullable=True)  # 模型描述
    remark = Column(Text, nullable=True)  # 备注说明
    status = Column(String(20), default="active", nullable=False)  # 状态：active/deprecated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 