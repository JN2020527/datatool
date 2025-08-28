from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RootBase(BaseModel):
    """词根基础模型"""
    name: str = Field(..., description="词根名称", min_length=1, max_length=64)
    remark: Optional[str] = Field(None, description="备注说明")
    tags: Optional[List[str]] = Field(None, description="标签列表")

class RootCreate(RootBase):
    """创建词根请求模型"""
    pass

class RootUpdate(BaseModel):
    """更新词根请求模型"""
    name: Optional[str] = Field(None, description="词根名称", min_length=1, max_length=64)
    remark: Optional[str] = Field(None, description="备注说明")
    tags: Optional[List[str]] = Field(None, description="标签列表")

class RootResponse(RootBase):
    """词根响应模型"""
    id: int
    normalized_name: str
    aliases: Optional[List[str]] = []
    usage_count: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class RootListResponse(BaseModel):
    """词根列表响应模型"""
    list: List[RootResponse]
    total: int
    page: int
    pageSize: int

class AliasCreate(BaseModel):
    """创建别名请求模型"""
    alias: str = Field(..., description="别名", min_length=1, max_length=64)

class AliasResponse(BaseModel):
    """别名响应模型"""
    id: int
    aliases: List[str]
    
    class Config:
        from_attributes = True

class RootImpactResponse(BaseModel):
    """词根影响面响应模型"""
    fields: List[dict] = Field(..., description="受影响的字段列表")
    models: List[dict] = Field(..., description="受影响的模型列表") 