from fastapi import FastAPI
from app.v1.router import api_v1_router
from app.core.exceptions import (
    DataDictException,
    data_dict_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(
    title="Data Dict Tool API", 
    version="0.1.0",
    description="数据字典工具API - 统一词根、字段、模型管理"
)

# 注册异常处理器
app.add_exception_handler(DataDictException, data_dict_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

@app.get("/health", tags=["system"]) 
def health_check():
    """健康检查接口"""
    return {"status": "ok", "message": "Data Dict Tool API is running"}

@app.get("/", tags=["system"])
def root():
    """根路径"""
    return {
        "message": "Data Dict Tool API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }

# 注册API路由
app.include_router(api_v1_router, prefix="/api/v1") 