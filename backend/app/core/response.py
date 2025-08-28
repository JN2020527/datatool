from typing import Generic, TypeVar, Optional, Any, Dict, List
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from fastapi import status

# 定义数据泛型类型
T = TypeVar('T')

class PaginationParams(BaseModel):
    """分页参数模型"""
    page: int = Field(1, ge=1, description="页码，从1开始")
    page_size: int = Field(20, ge=1, le=100, description="每页大小，最大100")

class PaginationResponse(BaseModel):
    """分页响应模型"""
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total: int = Field(..., description="总记录数")
    total_pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")

class BaseResponse(BaseModel, Generic[T]):
    """统一响应结构"""
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    error_code: Optional[str] = Field(None, description="错误代码")
    errors: Optional[List[str]] = Field(None, description="错误详情列表")

class ListResponse(BaseModel, Generic[T]):
    """列表响应结构"""
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: List[T] = Field(..., description="数据列表")
    pagination: PaginationResponse = Field(..., description="分页信息")

class ErrorResponse(BaseModel):
    """错误响应结构"""
    success: bool = Field(False, description="请求失败")
    message: str = Field(..., description="错误消息")
    error_code: str = Field(..., description="错误代码")
    errors: Optional[List[str]] = Field(None, description="错误详情列表")

# 预定义错误码
class ErrorCodes:
    """错误码定义"""
    # 通用错误 (1000-1999)
    VALIDATION_ERROR = "1000"
    INVALID_PARAMETER = "1001"
    RESOURCE_NOT_FOUND = "1002"
    UNAUTHORIZED = "1003"
    FORBIDDEN = "1004"
    INTERNAL_ERROR = "1005"
    
    # 词根相关错误 (2000-2999)
    ROOT_NAME_CONFLICT = "2000"
    ROOT_NOT_FOUND = "2001"
    ROOT_IN_USE = "2002"
    ROOT_NAME_INVALID = "2003"
    
    # 字段相关错误 (3000-3999)
    FIELD_NAME_CONFLICT = "3000"
    FIELD_NOT_FOUND = "3001"
    FIELD_IN_USE = "3002"
    FIELD_NAME_INVALID = "3003"
    ROOT_COMBINATION_REQUIRED = "3004"
    MISSING_ROOTS = "3005"
    
    # 模型相关错误 (4000-4999)
    MODEL_NAME_CONFLICT = "4000"
    MODEL_NOT_FOUND = "4001"
    FIELD_ALREADY_BOUND = "4002"
    FIELD_NOT_BOUND = "4003"
    
    # 导出相关错误 (5000-5999)
    EXPORT_FORMAT_NOT_SUPPORTED = "5000"
    EXPORT_FAILED = "5001"

# 预定义错误消息
class ErrorMessages:
    """错误消息定义"""
    MESSAGES = {
        # 通用错误
        ErrorCodes.VALIDATION_ERROR: "数据验证失败",
        ErrorCodes.INVALID_PARAMETER: "参数无效",
        ErrorCodes.RESOURCE_NOT_FOUND: "资源不存在",
        ErrorCodes.UNAUTHORIZED: "未授权访问",
        ErrorCodes.FORBIDDEN: "禁止访问",
        ErrorCodes.INTERNAL_ERROR: "内部服务器错误",
        
        # 词根相关错误
        ErrorCodes.ROOT_NAME_CONFLICT: "词根名称冲突",
        ErrorCodes.ROOT_NOT_FOUND: "词根不存在",
        ErrorCodes.ROOT_IN_USE: "词根正在使用中",
        ErrorCodes.ROOT_NAME_INVALID: "词根名称格式无效",
        
        # 字段相关错误
        ErrorCodes.FIELD_NAME_CONFLICT: "字段名称冲突",
        ErrorCodes.FIELD_NOT_FOUND: "字段不存在",
        ErrorCodes.FIELD_IN_USE: "字段正在使用中",
        ErrorCodes.FIELD_NAME_INVALID: "字段名称格式无效",
        ErrorCodes.ROOT_COMBINATION_REQUIRED: "字段必须基于词根组合创建",
        ErrorCodes.MISSING_ROOTS: "词根缺失",
        
        # 模型相关错误
        ErrorCodes.MODEL_NAME_CONFLICT: "模型名称冲突",
        ErrorCodes.MODEL_NOT_FOUND: "模型不存在",
        ErrorCodes.FIELD_ALREADY_BOUND: "字段已经绑定到该模型",
        ErrorCodes.FIELD_NOT_BOUND: "字段未绑定到该模型",
        
        # 导出相关错误
        ErrorCodes.EXPORT_FORMAT_NOT_SUPPORTED: "不支持的导出格式",
        ErrorCodes.EXPORT_FAILED: "导出失败",
    }
    
    @classmethod
    def get_message(cls, error_code: str) -> str:
        """获取错误消息"""
        return cls.MESSAGES.get(error_code, "未知错误")

# 响应工具函数
def success_response(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
    """成功响应"""
    return {
        "success": True,
        "message": message,
        "data": data,
        "error_code": None,
        "errors": None
    }

def error_response(
    error_code: str, 
    message: str = None, 
    errors: List[str] = None
) -> Dict[str, Any]:
    """错误响应"""
    if message is None:
        message = ErrorMessages.get_message(error_code)
    
    return {
        "success": False,
        "message": message,
        "data": None,
        "error_code": error_code,
        "errors": errors
    }

def pagination_response(
    data: List[Any],
    page: int,
    page_size: int,
    total: int,
    message: str = "查询成功"
) -> Dict[str, Any]:
    """分页响应"""
    total_pages = (total + page_size - 1) // page_size
    has_next = page < total_pages
    has_prev = page > 1
    
    pagination = PaginationResponse(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev
    )
    
    return {
        "success": True,
        "message": message,
        "data": data,
        "pagination": pagination.dict(),
        "error_code": None,
        "errors": None
    }

# 自定义JSON响应
class CustomJSONResponse(JSONResponse):
    """自定义JSON响应，支持统一响应结构"""
    
    def __init__(
        self,
        content: Any,
        status_code: int = status.HTTP_200_OK,
        headers: Optional[Dict[str, str]] = None,
        media_type: Optional[str] = None,
        background: Optional[Any] = None,
    ):
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background
        ) 