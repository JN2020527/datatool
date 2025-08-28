from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class FieldBase(BaseModel):
    """字段基础模型"""
    field_name: str = Field(..., description="字段名", min_length=1, max_length=128)
    meaning: str = Field(..., description="业务含义")
    data_type: str = Field(..., description="数据类型")
    root_list: List[str] = Field(..., description="使用的词根列表")
    remark: Optional[str] = Field(None, description="备注说明")

class FieldCreate(FieldBase):
    """创建字段请求模型"""
    pass

class FieldUpdate(BaseModel):
    """更新字段请求模型"""
    field_name: Optional[str] = Field(None, description="字段名", min_length=1, max_length=128)
    meaning: Optional[str] = Field(None, description="业务含义")
    data_type: Optional[str] = Field(None, description="数据类型")
    root_list: Optional[List[str]] = Field(None, description="使用的词根列表")
    remark: Optional[str] = Field(None, description="备注说明")

class FieldResponse(FieldBase):
    """字段响应模型"""
    id: int
    normalized_name: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class FieldListResponse(BaseModel):
    """字段列表响应模型"""
    list: List[FieldResponse]
    total: int
    page: int
    pageSize: int

class FieldStatusUpdate(BaseModel):
    """字段状态更新请求模型"""
    status: str = Field(..., description="新状态", pattern="^(active|deprecated)$")

class FieldUniqueCheck(BaseModel):
    """字段唯一性检查请求模型"""
    field_name: str = Field(..., description="要检查的字段名")

class FieldUniqueResponse(BaseModel):
    """字段唯一性检查响应模型"""
    unique: bool
    message: Optional[str] = None
    alternatives: Optional[List[str]] = None 