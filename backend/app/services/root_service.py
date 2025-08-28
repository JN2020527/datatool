from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import json

from app.models.root import Root
from app.models.field import Field
from app.models.model import Model
from app.models.model_field import ModelField
from app.core.normalization import normalize_name, validate_name
from app.core.conflict_checker import ConflictChecker
from app.schemas.root import RootCreate, RootUpdate

class RootService:
    """词根服务"""
    
    def __init__(self):
        self.conflict_checker = ConflictChecker()
    
    def create_root(self, db: Session, root_data: RootCreate) -> Tuple[Optional[Root], List[str]]:
        """
        创建词根
        
        Returns:
            (词根对象, 错误信息列表)
        """
        errors = []
        
        # 1. 规范化名称
        normalized_name = normalize_name(root_data.name)
        if not normalized_name:
            errors.append("词根名称不能为空")
            return None, errors
        
        # 2. 验证名称
        is_valid, error_msg = validate_name(normalized_name, max_length=64)
        if not is_valid:
            errors.append(error_msg)
            return None, errors
        
        # 3. 检查冲突
        existing_roots = self._get_all_roots(db)
        existing_fields = self._get_all_fields(db)
        
        has_conflict, conflicts, alternative = self.conflict_checker.check_root_conflicts(
            normalized_name, existing_roots, existing_fields
        )
        
        if has_conflict:
            errors.extend(conflicts)
            if alternative:
                errors.append(f"建议使用: {alternative}")
            return None, errors
        
        # 4. 创建词根
        try:
            db_root = Root(
                name=root_data.name,
                normalized_name=normalized_name,
                aliases=json.dumps([]),  # 初始化为空列表
                tags=json.dumps(root_data.tags or []),
                usage_count=0,
                status="active"
            )
            db.add(db_root)
            db.commit()
            db.refresh(db_root)
            return db_root, []
        except Exception as e:
            db.rollback()
            errors.append(f"创建词根失败: {str(e)}")
            return None, errors
    
    def get_roots(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[Root], int]:
        """获取词根列表"""
        query = db.query(Root)
        
        # 搜索过滤
        if search:
            query = query.filter(
                or_(
                    Root.name.contains(search),
                    Root.normalized_name.contains(search),
                    Root.remark.contains(search)
                )
            )
        
        # 状态过滤
        if status:
            query = query.filter(Root.status == status)
        
        total = query.count()
        roots = query.offset(skip).limit(limit).all()
        
        # 处理JSON字段
        for root in roots:
            if root.aliases:
                try:
                    root.aliases = json.loads(root.aliases)
                except:
                    root.aliases = []
            else:
                root.aliases = []
                
            if root.tags:
                try:
                    root.tags = json.loads(root.tags)
                except:
                    root.tags = []
            else:
                root.tags = []
        
        return roots, total
    
    def get_root(self, db: Session, root_id: int) -> Optional[Root]:
        """获取单个词根"""
        root = db.query(Root).filter(Root.id == root_id).first()
        if root:
            # 处理JSON字段
            if root.aliases:
                try:
                    root.aliases = json.loads(root.aliases)
                except:
                    root.aliases = []
            else:
                root.aliases = []
                
            if root.tags:
                try:
                    root.tags = json.loads(root.tags)
                except:
                    root.tags = []
            else:
                root.tags = []
        
        return root
    
    def update_root(self, db: Session, root_id: int, root_data: RootUpdate) -> Tuple[Optional[Root], List[str]]:
        """更新词根"""
        errors = []
        
        db_root = self.get_root(db, root_id)
        if not db_root:
            errors.append("词根不存在")
            return None, errors
        
        try:
            # 如果更新名称，需要检查冲突
            if root_data.name and root_data.name != db_root.name:
                normalized_name = normalize_name(root_data.name)
                is_valid, error_msg = validate_name(normalized_name, max_length=64)
                if not is_valid:
                    errors.append(error_msg)
                    return None, errors
                
                # 检查冲突（排除自己）
                existing_roots = [r for r in self._get_all_roots(db) if r.get("id") != root_id]
                existing_fields = self._get_all_fields(db)
                
                has_conflict, conflicts, alternative = self.conflict_checker.check_root_conflicts(
                    normalized_name, existing_roots, existing_fields
                )
                
                if has_conflict:
                    errors.extend(conflicts)
                    if alternative:
                        errors.append(f"建议使用: {alternative}")
                    return None, errors
                
                db_root.name = root_data.name
                db_root.normalized_name = normalized_name
            
            # 更新其他字段
            if root_data.remark is not None:
                db_root.remark = root_data.remark
            if root_data.tags is not None:
                db_root.tags = json.dumps(root_data.tags)
            
            db.commit()
            db.refresh(db_root)
            
            # 重新获取并处理JSON字段
            return self.get_root(db, root_id), []
            
        except Exception as e:
            db.rollback()
            errors.append(f"更新词根失败: {str(e)}")
            return None, errors
    
    def delete_root(self, db: Session, root_id: int) -> Tuple[bool, List[str]]:
        """删除词根"""
        errors = []
        
        db_root = self.get_root(db, root_id)
        if not db_root:
            errors.append("词根不存在")
            return False, errors
        
        # 检查是否被引用
        impact = self.get_root_impact(db, root_id)
        if impact["fields"] or impact["models"]:
            errors.append("词根正在被使用，无法删除")
            errors.append(f"影响字段: {len(impact['fields'])}个")
            errors.append(f"影响模型: {len(impact['models'])}个")
            return False, errors
        
        try:
            db.delete(db_root)
            db.commit()
            return True, []
        except Exception as e:
            db.rollback()
            errors.append(f"删除词根失败: {str(e)}")
            return False, errors
    
    def add_alias(self, db: Session, root_id: int, alias: str) -> Tuple[Optional[Root], List[str]]:
        """添加别名"""
        errors = []
        
        db_root = self.get_root(db, root_id)
        if not db_root:
            errors.append("词根不存在")
            return None, errors
        
        # 规范化别名
        normalized_alias = normalize_name(alias)
        if not normalized_alias:
            errors.append("别名不能为空")
            return None, errors
        
        # 检查别名是否与现有词根冲突
        existing_roots = self._get_all_roots(db)
        existing_fields = self._get_all_fields(db)
        
        has_conflict, conflicts, _ = self.conflict_checker.check_root_conflicts(
            normalized_alias, existing_roots, existing_fields
        )
        
        if has_conflict:
            errors.extend(conflicts)
            return None, errors
        
        try:
            # 解析现有别名
            current_aliases = json.loads(db_root.aliases) if db_root.aliases else []
            
            # 添加新别名
            if normalized_alias not in current_aliases:
                current_aliases.append(normalized_alias)
                db_root.aliases = json.dumps(current_aliases)
                db.commit()
                db.refresh(db_root)
            
            return self.get_root(db, root_id), []
            
        except Exception as e:
            db.rollback()
            errors.append(f"添加别名失败: {str(e)}")
            return None, errors
    
    def get_root_impact(self, db: Session, root_id: int) -> Dict:
        """获取词根影响面"""
        db_root = self.get_root(db, root_id)
        if not db_root:
            return {"fields": [], "models": []}
        
        # 查找使用该词根的字段
        fields = db.query(Field).filter(
            Field.root_list.contains(db_root.normalized_name)
        ).all()
        
        # 查找使用这些字段的模型
        model_ids = set()
        for field in fields:
            model_fields = db.query(ModelField).filter(ModelField.field_id == field.id).all()
            for mf in model_fields:
                model_ids.add(mf.model_id)
        
        models = []
        if model_ids:
            models = db.query(Model).filter(Model.id.in_(list(model_ids))).all()
        
        return {
            "fields": [{"id": f.id, "field_name": f.field_name} for f in fields],
            "models": [{"id": m.id, "model_name": m.model_name} for m in models]
        }
    
    def _get_all_roots(self, db: Session) -> List[Dict]:
        """获取所有词根（用于冲突检测）"""
        roots = db.query(Root).all()
        return [
            {
                "id": r.id,
                "name": r.name,
                "normalized_name": r.normalized_name
            }
            for r in roots
        ]
    
    def _get_all_fields(self, db: Session) -> List[Dict]:
        """获取所有字段（用于冲突检测）"""
        fields = db.query(Field).all()
        return [
            {
                "id": f.id,
                "field_name": f.field_name,
                "normalized_name": f.normalized_name
            }
            for f in fields
        ] 