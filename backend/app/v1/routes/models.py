from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.services.model_service import ModelService
from app.schemas.model import (
    ModelCreate, ModelUpdate, ModelResponse, ModelListResponse,
    ModelDetailResponse, ModelFieldBinding, ModelFieldUnbinding,
    ExportFormat, ExportResponse
)

router = APIRouter()
model_service = ModelService()

@router.get("", response_model=ModelListResponse)
def list_models(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[str] = Query(None, description="状态过滤"),
    db: Session = Depends(get_db)
):
    """获取模型列表"""
    skip = (page - 1) * page_size
    models, total = model_service.get_models(
        db, 
        skip=skip, 
        limit=page_size, 
        search=search, 
        status=status
    )
    
    return ModelListResponse(
        list=models,
        total=total,
        page=page,
        pageSize=page_size
    )

@router.post("", response_model=ModelResponse)
def create_model(model_data: ModelCreate, db: Session = Depends(get_db)):
    """创建模型"""
    model, errors = model_service.create_model(db, model_data)
    if not model:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    return model

@router.get("/{model_id}", response_model=ModelResponse)
def get_model(model_id: int, db: Session = Depends(get_db)):
    """获取模型详情"""
    model = model_service.get_model(db, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    return model

@router.get("/{model_id}/detail")
def get_model_detail(model_id: int, db: Session = Depends(get_db)):
    """获取模型详情（包含字段信息）"""
    model_detail = model_service.get_model_detail(db, model_id)
    if not model_detail:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    return model_detail

@router.put("/{model_id}", response_model=ModelResponse)
def update_model(model_id: int, model_data: ModelUpdate, db: Session = Depends(get_db)):
    """更新模型"""
    model, errors = model_service.update_model(db, model_id, model_data)
    if not model:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    return model

@router.delete("/{model_id}")
def delete_model(model_id: int, db: Session = Depends(get_db)):
    """删除模型"""
    success, errors = model_service.delete_model(db, model_id)
    if not success:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    return {"message": "模型删除成功"}

@router.post("/{model_id}/fields")
def bind_field_to_model(
    model_id: int, 
    binding_data: ModelFieldBinding, 
    db: Session = Depends(get_db)
):
    """绑定字段到模型"""
    success, errors = model_service.bind_field(db, model_id, binding_data)
    if not success:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    return {"message": "字段绑定成功"}

@router.delete("/{model_id}/fields")
def unbind_field_from_model(
    model_id: int, 
    unbinding_data: ModelFieldUnbinding, 
    db: Session = Depends(get_db)
):
    """从模型解绑字段"""
    success, errors = model_service.unbind_field(db, model_id, unbinding_data)
    if not success:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    return {"message": "字段解绑成功"}

@router.post("/{model_id}/export")
def export_model(
    model_id: int, 
    export_data: ExportFormat, 
    db: Session = Depends(get_db)
):
    """导出模型"""
    content, filename, errors = model_service.export_model(db, model_id, export_data)
    if not content:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    return ExportResponse(
        content=content,
        filename=filename,
        format=export_data.format
    ) 