from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.services.field_service import FieldService
from app.schemas.field import (
    FieldCreate, FieldUpdate, FieldResponse, FieldListResponse,
    FieldStatusUpdate, FieldUniqueCheck, FieldUniqueResponse
)

router = APIRouter()
field_service = FieldService()

@router.get("", response_model=FieldListResponse)
def list_fields(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[str] = Query(None, description="状态过滤"),
    root_filter: Optional[str] = Query(None, description="词根过滤"),
    db: Session = Depends(get_db)
):
    """获取字段列表"""
    skip = (page - 1) * page_size
    fields, total = field_service.get_fields(
        db, 
        skip=skip, 
        limit=page_size, 
        search=search, 
        status=status,
        root_filter=root_filter
    )
    
    return FieldListResponse(
        list=fields,
        total=total,
        page=page,
        pageSize=page_size
    )

@router.post("", response_model=FieldResponse)
def create_field(field_data: FieldCreate, db: Session = Depends(get_db)):
    """创建字段（强制词根组合）"""
    field, errors = field_service.create_field(db, field_data)
    if not field:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    return field

@router.get("/{field_id}", response_model=FieldResponse)
def get_field(field_id: int, db: Session = Depends(get_db)):
    """获取字段详情"""
    field = field_service.get_field(db, field_id)
    if not field:
        raise HTTPException(status_code=404, detail="字段不存在")
    
    return field

@router.put("/{field_id}", response_model=FieldResponse)
def update_field(field_id: int, field_data: FieldUpdate, db: Session = Depends(get_db)):
    """更新字段"""
    field, errors = field_service.update_field(db, field_id, field_data)
    if not field:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    return field

@router.delete("/{field_id}")
def delete_field(field_id: int, db: Session = Depends(get_db)):
    """删除字段"""
    success, errors = field_service.delete_field(db, field_id)
    if not success:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    return {"message": "字段删除成功"}

@router.patch("/{field_id}/status")
def update_field_status(field_id: int, status_data: FieldStatusUpdate, db: Session = Depends(get_db)):
    """更新字段状态"""
    success, errors = field_service.update_field_status(db, field_id, status_data)
    if not success:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    return {"message": "字段状态更新成功"}

@router.post("/check-unique", response_model=FieldUniqueResponse)
def check_field_unique(check_data: FieldUniqueCheck, db: Session = Depends(get_db)):
    """检查字段唯一性"""
    is_unique, message, alternatives = field_service.check_field_unique(db, check_data.field_name)
    
    return FieldUniqueResponse(
        unique=is_unique,
        message=message,
        alternatives=alternatives
    )

@router.get("/by-roots/{root_names}")
def get_fields_by_roots(
    root_names: str,
    db: Session = Depends(get_db)
):
    """根据词根组合查找字段"""
    # 解析词根名称（用逗号分隔）
    root_list = [r.strip() for r in root_names.split(",") if r.strip()]
    
    if not root_list:
        raise HTTPException(status_code=400, detail="请提供有效的词根名称")
    
    fields = field_service.get_field_by_roots(db, root_list)
    
    return {
        "root_names": root_list,
        "fields": [
            {
                "id": f.id,
                "field_name": f.field_name,
                "meaning": f.meaning,
                "data_type": f.data_type,
                "root_list": f.root_list,
                "status": f.status
            }
            for f in fields
        ]
    } 