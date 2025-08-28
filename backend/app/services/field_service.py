from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import json

from app.models.field import Field
from app.models.root import Root
from app.models.model import Model
from app.models.model_field import ModelField
from app.core.normalization import normalize_name, validate_name
from app.core.conflict_checker import ConflictChecker
from app.schemas.field import FieldCreate, FieldUpdate, FieldStatusUpdate

class FieldService:
    """字段服务"""
    
    def __init__(self):
        self.conflict_checker = ConflictChecker()
    
    def create_field(self, db: Session, field_data: FieldCreate) -> Tuple[Optional[Field], List[str]]:
        """
        创建字段（强制词根组合）
        
        Returns:
            (字段对象, 错误信息列表)
        """
        errors = []
        
        # 1. 验证词根列表
        if not field_data.root_list:
            errors.append("字段必须基于词根组合创建")
            return None, errors
        
        # 2. 检查所有词根是否存在
        missing_roots = []
        for root_name in field_data.root_list:
            root = db.query(Root).filter(Root.normalized_name == root_name).first()
            if not root:
                missing_roots.append(root_name)
        
        if missing_roots:
            errors.append(f"以下词根不存在: {', '.join(missing_roots)}")
            errors.append("请先创建缺失的词根")
            return None, errors
        
        # 3. 生成字段名（基于词根组合）
        generated_name = "_".join(field_data.root_list)
        if field_data.field_name != generated_name:
            errors.append(f"字段名必须基于词根组合: {generated_name}")
            return None, errors
        
        # 4. 规范化名称
        normalized_name = normalize_name(field_data.field_name)
        if not normalized_name:
            errors.append("字段名称不能为空")
            return None, errors
        
        # 5. 验证名称
        is_valid, error_msg = validate_name(normalized_name, max_length=128)
        if not is_valid:
            errors.append(error_msg)
            return None, errors
        
        # 6. 检查冲突
        existing_fields = self._get_all_fields(db)
        has_conflict, conflicts, alternative = self.conflict_checker.check_field_conflicts(
            normalized_name, existing_fields
        )
        
        if has_conflict:
            errors.extend(conflicts)
            if alternative:
                errors.append(f"建议使用: {alternative}")
            return None, errors
        
        # 7. 创建字段
        try:
            db_field = Field(
                field_name=field_data.field_name,
                normalized_name=normalized_name,
                meaning=field_data.meaning,
                data_type=field_data.data_type,
                root_list=json.dumps(field_data.root_list),
                remark=field_data.remark,
                status="active"
            )
            db.add(db_field)
            db.commit()
            db.refresh(db_field)
            
            # 更新词根使用计数
            self._update_root_usage_count(db, field_data.root_list, increment=True)
            
            return db_field, []
        except Exception as e:
            db.rollback()
            errors.append(f"创建字段失败: {str(e)}")
            return None, errors
    
    def get_fields(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
        root_filter: Optional[str] = None
    ) -> Tuple[List[Field], int]:
        """获取字段列表"""
        query = db.query(Field)
        
        # 搜索过滤
        if search:
            query = query.filter(
                or_(
                    Field.field_name.contains(search),
                    Field.normalized_name.contains(search),
                    Field.meaning.contains(search),
                    Field.remark.contains(search)
                )
            )
        
        # 状态过滤
        if status:
            query = query.filter(Field.status == status)
        
        # 词根过滤
        if root_filter:
            query = query.filter(Field.root_list.contains(root_filter))
        
        total = query.count()
        fields = query.offset(skip).limit(limit).all()
        
        # 处理JSON字段
        for field in fields:
            if field.root_list:
                try:
                    field.root_list = json.loads(field.root_list)
                except:
                    field.root_list = []
            else:
                field.root_list = []
        
        return fields, total
    
    def get_field(self, db: Session, field_id: int) -> Optional[Field]:
        """获取单个字段"""
        field = db.query(Field).filter(Field.id == field_id).first()
        if field and field.root_list:
            try:
                field.root_list = json.loads(field.root_list)
            except:
                field.root_list = []
        return field
    
    def update_field(self, db: Session, field_id: int, field_data: FieldUpdate) -> Tuple[Optional[Field], List[str]]:
        """更新字段"""
        errors = []
        
        db_field = self.get_field(db, field_id)
        if not db_field:
            errors.append("字段不存在")
            return None, errors
        
        try:
            old_root_list = db_field.root_list
            
            # 如果更新字段名，需要检查冲突
            if field_data.field_name and field_data.field_name != db_field.field_name:
                normalized_name = normalize_name(field_data.field_name)
                is_valid, error_msg = validate_name(normalized_name, max_length=128)
                if not is_valid:
                    errors.append(error_msg)
                    return None, errors
                
                # 检查冲突（排除自己）
                existing_fields = [f for f in self._get_all_fields(db) if f.get("id") != field_id]
                has_conflict, conflicts, alternative = self.conflict_checker.check_field_conflicts(
                    normalized_name, existing_fields
                )
                
                if has_conflict:
                    errors.extend(conflicts)
                    if alternative:
                        errors.append(f"建议使用: {alternative}")
                    return None, errors
                
                db_field.field_name = field_data.field_name
                db_field.normalized_name = normalized_name
            
            # 更新其他字段
            if field_data.meaning is not None:
                db_field.meaning = field_data.meaning
            if field_data.data_type is not None:
                db_field.data_type = field_data.data_type
            if field_data.remark is not None:
                db_field.remark = field_data.remark
            
            # 如果更新词根列表，需要验证和更新计数
            if field_data.root_list is not None:
                # 验证新词根列表
                missing_roots = []
                for root_name in field_data.root_list:
                    root = db.query(Root).filter(Root.normalized_name == root_name).first()
                    if not root:
                        missing_roots.append(root_name)
                
                if missing_roots:
                    errors.append(f"以下词根不存在: {', '.join(missing_roots)}")
                    return None, errors
                
                db_field.root_list = json.dumps(field_data.root_list)
                
                # 更新词根使用计数
                self._update_root_usage_count(db, old_root_list, increment=False)
                self._update_root_usage_count(db, field_data.root_list, increment=True)
            
            db.commit()
            db.refresh(db_field)
            
            # 重新获取并处理JSON字段
            return self.get_field(db, field_id), []
            
        except Exception as e:
            db.rollback()
            errors.append(f"更新字段失败: {str(e)}")
            return None, errors
    
    def delete_field(self, db: Session, field_id: int) -> Tuple[bool, List[str]]:
        """删除字段"""
        errors = []
        
        db_field = self.get_field(db, field_id)
        if not db_field:
            errors.append("字段不存在")
            return False, errors
        
        # 检查是否被模型引用
        model_fields = db.query(ModelField).filter(ModelField.field_id == field_id).all()
        if model_fields:
            errors.append("字段正在被模型使用，无法删除")
            errors.append(f"影响模型: {len(model_fields)}个")
            return False, errors
        
        try:
            # 更新词根使用计数
            if db_field.root_list:
                self._update_root_usage_count(db, db_field.root_list, increment=False)
            
            db.delete(db_field)
            db.commit()
            return True, []
        except Exception as e:
            db.rollback()
            errors.append(f"删除字段失败: {str(e)}")
            return False, errors
    
    def update_field_status(self, db: Session, field_id: int, status_data: FieldStatusUpdate) -> Tuple[bool, List[str]]:
        """更新字段状态"""
        errors = []
        
        db_field = db.query(Field).filter(Field.id == field_id).first()
        if not db_field:
            errors.append("字段不存在")
            return False, errors
        
        try:
            db_field.status = status_data.status
            db.commit()
            return True, []
        except Exception as e:
            db.rollback()
            errors.append(f"更新字段状态失败: {str(e)}")
            return False, errors
    
    def check_field_unique(self, db: Session, field_name: str) -> Tuple[bool, Optional[str], List[str]]:
        """检查字段唯一性"""
        normalized_name = normalize_name(field_name)
        if not normalized_name:
            return False, "字段名称不能为空", []
        
        # 验证名称格式
        is_valid, error_msg = validate_name(normalized_name, max_length=128)
        if not is_valid:
            return False, error_msg, []
        
        # 检查是否已存在
        existing_field = db.query(Field).filter(Field.normalized_name == normalized_name).first()
        if existing_field:
            alternatives = self.conflict_checker._generate_field_alternatives(normalized_name, [existing_field.normalized_name])
            return False, f"字段名已存在: {existing_field.field_name} (ID: {existing_field.id})", alternatives
        
        return True, "字段名可用", []
    
    def get_field_by_roots(self, db: Session, root_names: List[str]) -> List[Field]:
        """根据词根组合查找字段"""
        if not root_names:
            return []
        
        # 构建查询条件：字段的词根列表包含所有指定的词根
        query = db.query(Field)
        for root_name in root_names:
            query = query.filter(Field.root_list.contains(root_name))
        
        fields = query.all()
        
        # 处理JSON字段
        for field in fields:
            if field.root_list:
                try:
                    field.root_list = json.loads(field.root_list)
                except:
                    field.root_list = []
            else:
                field.root_list = []
        
        return fields
    
    def _update_root_usage_count(self, db: Session, root_names: List[str], increment: bool):
        """更新词根使用计数"""
        if not root_names:
            return
        
        for root_name in root_names:
            root = db.query(Root).filter(Root.normalized_name == root_name).first()
            if root:
                if increment:
                    root.usage_count += 1
                else:
                    root.usage_count = max(0, root.usage_count - 1)
        
        try:
            db.commit()
        except:
            db.rollback()
    
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