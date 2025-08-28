from typing import List, Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.response import error_response, ErrorCodes

class DataDictException(Exception):
    """数据字典工具基础异常"""
    
    def __init__(
        self, 
        error_code: str, 
        message: str = None, 
        errors: List[str] = None,
        status_code: int = 400
    ):
        self.error_code = error_code
        self.message = message
        self.errors = errors or []
        self.status_code = status_code
        super().__init__(message)

class RootException(DataDictException):
    """词根相关异常"""
    pass

class FieldException(DataDictException):
    """字段相关异常"""
    pass

class ModelException(DataDictException):
    """模型相关异常"""
    pass

class ValidationException(DataDictException):
    """数据验证异常"""
    pass

# 具体异常类
class RootNameConflictException(RootException):
    """词根名称冲突异常"""
    def __init__(self, root_name: str, existing_id: int, alternative: str = None):
        message = f"词根名称冲突: {root_name} (ID: {existing_id})"
        if alternative:
            message += f"，建议使用: {alternative}"
        
        errors = [message]
        if alternative:
            errors.append(f"建议使用: {alternative}")
        
        super().__init__(
            error_code=ErrorCodes.ROOT_NAME_CONFLICT,
            message=message,
            errors=errors,
            status_code=400
        )

class RootNotFoundException(RootException):
    """词根不存在异常"""
    def __init__(self, root_name: str):
        message = f"词根不存在: {root_name}"
        super().__init__(
            error_code=ErrorCodes.ROOT_NOT_FOUND,
            message=message,
            errors=[message],
            status_code=404
        )

class RootInUseException(RootException):
    """词根正在使用中异常"""
    def __init__(self, root_name: str, usage_count: int):
        message = f"词根正在使用中: {root_name} (使用次数: {usage_count})"
        super().__init__(
            error_code=ErrorCodes.ROOT_IN_USE,
            message=message,
            errors=[message],
            status_code=400
        )

class FieldNameConflictException(FieldException):
    """字段名称冲突异常"""
    def __init__(self, field_name: str, existing_id: int, alternatives: List[str] = None):
        message = f"字段名称冲突: {field_name} (ID: {existing_id})"
        errors = [message]
        
        if alternatives:
            errors.append(f"建议使用: {alternatives}")
        
        super().__init__(
            error_code=ErrorCodes.FIELD_NAME_CONFLICT,
            message=message,
            errors=errors,
            status_code=400
        )

class FieldNotFoundException(FieldException):
    """字段不存在异常"""
    def __init__(self, field_name: str):
        message = f"字段不存在: {field_name}"
        super().__init__(
            error_code=ErrorCodes.FIELD_NOT_FOUND,
            message=message,
            errors=[message],
            status_code=404
        )

class RootCombinationRequiredException(FieldException):
    """字段必须基于词根组合创建异常"""
    def __init__(self, field_name: str):
        message = f"字段必须基于词根组合创建: {field_name}"
        super().__init__(
            error_code=ErrorCodes.ROOT_COMBINATION_REQUIRED,
            message=message,
            errors=[message],
            status_code=400
        )

class MissingRootsException(FieldException):
    """词根缺失异常"""
    def __init__(self, missing_roots: List[str]):
        message = f"以下词根不存在: {', '.join(missing_roots)}"
        errors = [message, "请先创建缺失的词根"]
        super().__init__(
            error_code=ErrorCodes.MISSING_ROOTS,
            message=message,
            errors=errors,
            status_code=400
        )

class ModelNameConflictException(ModelException):
    """模型名称冲突异常"""
    def __init__(self, model_name: str, existing_id: int):
        message = f"模型名称已存在: {model_name} (ID: {existing_id})"
        super().__init__(
            error_code=ErrorCodes.MODEL_NAME_CONFLICT,
            message=message,
            errors=[message],
            status_code=400
        )

class ModelNotFoundException(ModelException):
    """模型不存在异常"""
    def __init__(self, model_name: str):
        message = f"模型不存在: {model_name}"
        super().__init__(
            error_code=ErrorCodes.MODEL_NOT_FOUND,
            message=message,
            errors=[message],
            status_code=404
        )

class FieldAlreadyBoundException(ModelException):
    """字段已经绑定异常"""
    def __init__(self, field_name: str, model_name: str):
        message = f"字段已经绑定到该模型: {field_name} -> {model_name}"
        super().__init__(
            error_code=ErrorCodes.FIELD_ALREADY_BOUND,
            message=message,
            errors=[message],
            status_code=400
        )

class FieldNotBoundException(ModelException):
    """字段未绑定异常"""
    def __init__(self, field_name: str, model_name: str):
        message = f"字段未绑定到该模型: {field_name} -> {model_name}"
        super().__init__(
            error_code=ErrorCodes.FIELD_NOT_BOUND,
            message=message,
            errors=[message],
            status_code=400
        )

# 异常处理器
async def data_dict_exception_handler(request: Request, exc: DataDictException):
    """数据字典工具异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            error_code=exc.error_code,
            message=exc.message,
            errors=exc.errors
        )
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = f"{field}: {error['msg']}"
        errors.append(message)
    
    return JSONResponse(
        status_code=422,
        content=error_response(
            error_code=ErrorCodes.VALIDATION_ERROR,
            message="数据验证失败",
            errors=errors
        )
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            error_code=ErrorCodes.RESOURCE_NOT_FOUND,
            message=exc.detail,
            errors=[exc.detail]
        )
    )

async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    return JSONResponse(
        status_code=500,
        content=error_response(
            error_code=ErrorCodes.INTERNAL_ERROR,
            message="内部服务器错误",
            errors=[str(exc)]
        )
    ) 