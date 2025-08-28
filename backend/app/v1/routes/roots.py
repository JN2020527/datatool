from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.services.root_service import RootService
from app.schemas.root import (
    RootCreate, RootUpdate, RootResponse, RootListResponse,
    AliasCreate, AliasResponse, RootImpactResponse
)

router = APIRouter()
root_service = RootService()

@router.get("", response_model=RootListResponse)
def list_roots(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[str] = Query(None, description="状态过滤"),
    db: Session = Depends(get_db)
):
    """获取词根列表"""
    skip = (page - 1) * page_size
    roots, total = root_service.get_roots(db, skip=skip, limit=page_size, search=search, status=status)
    
    return RootListResponse(
        list=roots,
        total=total,
        page=page,
        pageSize=page_size
    )

@router.post("", response_model=RootResponse)
def create_root(root_data: RootCreate, db: Session = Depends(get_db)):
    """创建词根"""
    root, errors = root_service.create_root(db, root_data)
    if not root:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    return root

@router.get("/{root_id}", response_model=RootResponse)
def get_root(root_id: int, db: Session = Depends(get_db)):
    """获取词根详情"""
    root = root_service.get_root(db, root_id)
    if not root:
        raise HTTPException(status_code=404, detail="词根不存在")
    
    return root

@router.put("/{root_id}", response_model=RootResponse)
def update_root(root_id: int, root_data: RootUpdate, db: Session = Depends(get_db)):
    """更新词根"""
    root, errors = root_service.update_root(db, root_id, root_data)
    if not root:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    return root

@router.delete("/{root_id}")
def delete_root(root_id: int, db: Session = Depends(get_db)):
    """删除词根"""
    success, errors = root_service.delete_root(db, root_id)
    if not success:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    return {"message": "词根删除成功"}

@router.post("/{root_id}/aliases", response_model=AliasResponse)
def add_alias(root_id: int, alias_data: AliasCreate, db: Session = Depends(get_db)):
    """添加别名"""
    root, errors = root_service.add_alias(db, root_id, alias_data.alias)
    if not root:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    # 解析别名列表
    import json
    aliases = json.loads(root.aliases) if root.aliases else []
    
    return AliasResponse(id=root.id, aliases=aliases)

@router.get("/{root_id}/impact", response_model=RootImpactResponse)
def root_impact(root_id: int, db: Session = Depends(get_db)):
    """获取词根影响面"""
    impact = root_service.get_root_impact(db, root_id)
    return RootImpactResponse(**impact) 