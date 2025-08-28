from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class Lineage(Base):
    __tablename__ = "lineages"
    
    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False, index=True)  # 字段ID
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False, index=True)  # 模型ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # 引用关系建立时间 