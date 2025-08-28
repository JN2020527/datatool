from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class ModelField(Base):
    __tablename__ = "model_fields"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False, index=True)  # 模型ID
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False, index=True)  # 字段ID
    pos = Column(Integer, nullable=False, default=0)  # 字段顺序
    required = Column(String(5), nullable=False, default="false")  # 是否必填：true/false
    default_value = Column(Text, nullable=True)  # 默认值
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 