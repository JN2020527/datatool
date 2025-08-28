from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ModelBase(BaseModel):
    """模型基础模型"""
    model_name: str = Field(..., description="模型名称", min_length=1, max_length=128)
    description: Optional[str] = Field(None, description="模型描述")
    remark: Optional[str] = Field(None, description="备注说明")

class ModelCreate(ModelBase):
    """创建模型请求模型"""
    pass

class ModelUpdate(BaseModel):
    """更新模型请求模型"""
    model_name: Optional[str] = Field(None, description="模型名称", min_length=1, max_length=128)
    description: Optional[str] = Field(None, description="模型描述")
    remark: Optional[str] = Field(None, description="备注说明")

class ModelResponse(ModelBase):
    """模型响应模型"""
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ModelListResponse(BaseModel):
    """模型列表响应模型"""
    list: List[ModelResponse]
    total: int
    page: int
    pageSize: int

class ModelFieldBinding(BaseModel):
    """模型字段绑定请求模型"""
    field_id: int = Field(..., description="字段ID")
    pos: int = Field(0, description="字段位置", ge=0)
    required: str = Field("false", description="是否必填", pattern="^(true|false)$")
    default_value: Optional[str] = Field(None, description="默认值")

class ModelFieldUnbinding(BaseModel):
    """模型字段解绑请求模型"""
    field_id: int = Field(..., description="字段ID")

class ModelFieldResponse(BaseModel):
    """模型字段响应模型"""
    id: int
    field_id: int
    field_name: str
    meaning: str
    data_type: str
    pos: int
    required: str
    default_value: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ModelDetailResponse(ModelResponse):
    """模型详情响应模型（包含字段信息）"""
    fields: List[ModelFieldResponse] = []

class ExportFormat(BaseModel):
    """导出格式请求模型"""
    format: str = Field(..., description="导出格式", pattern="^(sql|excel)$")
    include_ddl: bool = Field(True, description="是否包含DDL语句")
    include_data: bool = Field(False, description="是否包含示例数据")

class ExportResponse(BaseModel):
    """导出响应模型"""
    content: str
    filename: str
    format: str 