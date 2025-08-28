from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import json

from app.models.model import Model
from app.models.field import Field
from app.models.model_field import ModelField
from app.models.lineage import Lineage
from app.core.normalization import normalize_name, validate_name
from app.schemas.model import ModelCreate, ModelUpdate, ModelFieldBinding, ModelFieldUnbinding, ExportFormat

class ModelService:
    """模型服务"""
    
    def create_model(self, db: Session, model_data: ModelCreate) -> Tuple[Optional[Model], List[str]]:
        """
        创建模型
        
        Returns:
            (模型对象, 错误信息列表)
        """
        errors = []
        
        # 1. 规范化名称
        normalized_name = normalize_name(model_data.model_name)
        if not normalized_name:
            errors.append("模型名称不能为空")
            return None, errors
        
        # 2. 验证名称
        is_valid, error_msg = validate_name(normalized_name, max_length=128)
        if not is_valid:
            errors.append(error_msg)
            return None, errors
        
        # 3. 检查名称是否已存在
        existing_model = db.query(Model).filter(Model.model_name == model_data.model_name).first()
        if existing_model:
            errors.append(f"模型名称已存在: {existing_model.model_name} (ID: {existing_model.id})")
            return None, errors
        
        # 4. 创建模型
        try:
            db_model = Model(
                model_name=model_data.model_name,
                description=model_data.description,
                remark=model_data.remark,
                status="active"
            )
            db.add(db_model)
            db.commit()
            db.refresh(db_model)
            return db_model, []
        except Exception as e:
            db.rollback()
            errors.append(f"创建模型失败: {str(e)}")
            return None, errors
    
    def get_models(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[Model], int]:
        """获取模型列表"""
        query = db.query(Model)
        
        # 搜索过滤
        if search:
            query = query.filter(
                or_(
                    Model.model_name.contains(search),
                    Model.description.contains(search),
                    Model.remark.contains(search)
                )
            )
        
        # 状态过滤
        if status:
            query = query.filter(Model.status == status)
        
        total = query.count()
        models = query.offset(skip).limit(limit).all()
        
        return models, total
    
    def get_model(self, db: Session, model_id: int) -> Optional[Model]:
        """获取单个模型"""
        return db.query(Model).filter(Model.id == model_id).first()
    
    def get_model_detail(self, db: Session, model_id: int) -> Optional[Dict]:
        """获取模型详情（包含字段信息）"""
        model = self.get_model(db, model_id)
        if not model:
            return None
        
        # 获取模型字段
        model_fields = db.query(ModelField).filter(
            ModelField.model_id == model_id
        ).order_by(ModelField.pos).all()
        
        # 获取字段详细信息
        fields = []
        for mf in model_fields:
            field = db.query(Field).filter(Field.id == mf.field_id).first()
            if field:
                fields.append({
                    "id": mf.id,
                    "field_id": mf.field_id,
                    "field_name": field.field_name,
                    "meaning": field.meaning,
                    "data_type": field.data_type,
                    "pos": mf.pos,
                    "required": mf.required,
                    "default_value": mf.default_value,
                    "created_at": mf.created_at
                })
        
        return {
            "id": model.id,
            "model_name": model.model_name,
            "description": model.description,
            "remark": model.remark,
            "status": model.status,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
            "fields": fields
        }
    
    def update_model(self, db: Session, model_id: int, model_data: ModelUpdate) -> Tuple[Optional[Model], List[str]]:
        """更新模型"""
        errors = []
        
        db_model = self.get_model(db, model_id)
        if not db_model:
            errors.append("模型不存在")
            return None, errors
        
        try:
            # 如果更新名称，需要检查冲突
            if model_data.model_name and model_data.model_name != db_model.model_name:
                normalized_name = normalize_name(model_data.model_name)
                is_valid, error_msg = validate_name(normalized_name, max_length=128)
                if not is_valid:
                    errors.append(error_msg)
                    return None, errors
                
                # 检查名称是否已存在
                existing_model = db.query(Model).filter(
                    and_(
                        Model.model_name == model_data.model_name,
                        Model.id != model_id
                    )
                ).first()
                if existing_model:
                    errors.append(f"模型名称已存在: {existing_model.model_name} (ID: {existing_model.id})")
                    return None, errors
                
                db_model.model_name = model_data.model_name
            
            # 更新其他字段
            if model_data.description is not None:
                db_model.description = model_data.description
            if model_data.remark is not None:
                db_model.remark = model_data.remark
            
            db.commit()
            db.refresh(db_model)
            return db_model, []
            
        except Exception as e:
            db.rollback()
            errors.append(f"更新模型失败: {str(e)}")
            return None, errors
    
    def delete_model(self, db: Session, model_id: int) -> Tuple[bool, List[str]]:
        """删除模型"""
        errors = []
        
        db_model = self.get_model(db, model_id)
        if not db_model:
            errors.append("模型不存在")
            return False, errors
        
        try:
            # 删除模型字段关联
            db.query(ModelField).filter(ModelField.model_id == model_id).delete()
            
            # 删除血缘关系
            db.query(Lineage).filter(Lineage.model_id == model_id).delete()
            
            # 删除模型
            db.delete(db_model)
            db.commit()
            return True, []
        except Exception as e:
            db.rollback()
            errors.append(f"删除模型失败: {str(e)}")
            return False, errors
    
    def bind_field(self, db: Session, model_id: int, binding_data: ModelFieldBinding) -> Tuple[bool, List[str]]:
        """绑定字段到模型"""
        errors = []
        
        # 检查模型是否存在
        model = self.get_model(db, model_id)
        if not model:
            errors.append("模型不存在")
            return False, errors
        
        # 检查字段是否存在
        field = db.query(Field).filter(Field.id == binding_data.field_id).first()
        if not field:
            errors.append("字段不存在")
            return False, errors
        
        # 检查字段是否已经绑定
        existing_binding = db.query(ModelField).filter(
            and_(
                ModelField.model_id == model_id,
                ModelField.field_id == binding_data.field_id
            )
        ).first()
        
        if existing_binding:
            errors.append("字段已经绑定到该模型")
            return False, errors
        
        try:
            # 创建字段绑定
            model_field = ModelField(
                model_id=model_id,
                field_id=binding_data.field_id,
                pos=binding_data.pos,
                required=binding_data.required,
                default_value=binding_data.default_value
            )
            db.add(model_field)
            
            # 创建血缘关系
            lineage = Lineage(
                field_id=binding_data.field_id,
                model_id=model_id
            )
            db.add(lineage)
            
            db.commit()
            return True, []
            
        except Exception as e:
            db.rollback()
            errors.append(f"绑定字段失败: {str(e)}")
            return False, errors
    
    def unbind_field(self, db: Session, model_id: int, unbinding_data: ModelFieldUnbinding) -> Tuple[bool, List[str]]:
        """从模型解绑字段"""
        errors = []
        
        # 检查模型是否存在
        model = self.get_model(db, model_id)
        if not model:
            errors.append("模型不存在")
            return False, errors
        
        try:
            # 删除字段绑定
            result = db.query(ModelField).filter(
                and_(
                    ModelField.model_id == model_id,
                    ModelField.field_id == unbinding_data.field_id
                )
            ).delete()
            
            if result == 0:
                errors.append("字段未绑定到该模型")
                return False, errors
            
            # 删除血缘关系
            db.query(Lineage).filter(
                and_(
                    Lineage.model_id == model_id,
                    Lineage.field_id == unbinding_data.field_id
                )
            ).delete()
            
            db.commit()
            return True, []
            
        except Exception as e:
            db.rollback()
            errors.append(f"解绑字段失败: {str(e)}")
            return False, errors
    
    def export_model(self, db: Session, model_id: int, export_data: ExportFormat) -> Tuple[Optional[str], Optional[str], List[str]]:
        """导出模型"""
        errors = []
        
        model_detail = self.get_model_detail(db, model_id)
        if not model_detail:
            errors.append("模型不存在")
            return None, None, errors
        
        try:
            if export_data.format == "sql":
                content = self._generate_sql_ddl(model_detail, export_data.include_ddl, export_data.include_data)
                filename = f"{model_detail['model_name']}.sql"
            elif export_data.format == "excel":
                content = self._generate_excel_content(model_detail)
                filename = f"{model_detail['model_name']}.csv"
            else:
                errors.append("不支持的导出格式")
                return None, None, errors
            
            return content, filename, []
            
        except Exception as e:
            errors.append(f"导出失败: {str(e)}")
            return None, None, errors
    
    def _generate_sql_ddl(self, model_detail: Dict, include_ddl: bool, include_data: bool) -> str:
        """生成SQL DDL语句"""
        lines = []
        
        if include_ddl:
            # 创建表语句
            lines.append(f"-- 创建表: {model_detail['model_name']}")
            lines.append(f"-- 描述: {model_detail['description'] or '无描述'}")
            lines.append(f"CREATE TABLE {model_detail['model_name']} (")
            
            # 字段定义
            field_lines = []
            for field in model_detail['fields']:
                field_def = f"    {field['field_name']} {field['data_type'].upper()}"
                if field['required'] == "true":
                    field_def += " NOT NULL"
                if field['default_value']:
                    field_def += f" DEFAULT '{field['default_value']}'"
                field_def += f" COMMENT '{field['meaning']}'"
                field_lines.append(field_def)
            
            lines.append(",\n".join(field_lines))
            lines.append(");")
            lines.append("")
        
        if include_data:
            # 插入示例数据
            lines.append("-- 示例数据")
            lines.append(f"INSERT INTO {model_detail['model_name']} (")
            field_names = [field['field_name'] for field in model_detail['fields']]
            lines.append("    " + ", ".join(field_names))
            lines.append(") VALUES (")
            
            # 示例值
            sample_values = []
            for field in model_detail['fields']:
                if field['data_type'].lower() in ['int', 'bigint', 'smallint']:
                    sample_values.append("1")
                elif field['data_type'].lower() in ['varchar', 'char', 'text']:
                    sample_values.append(f"'{field['meaning']}'")
                elif field['data_type'].lower() in ['datetime', 'timestamp']:
                    sample_values.append("CURRENT_TIMESTAMP")
                else:
                    sample_values.append("NULL")
            
            lines.append("    " + ", ".join(sample_values))
            lines.append(");")
        
        return "\n".join(lines)
    
    def _generate_excel_content(self, model_detail: Dict) -> str:
        """生成Excel/CSV内容"""
        lines = []
        
        # 表头
        headers = ["字段名", "数据类型", "业务含义", "是否必填", "默认值", "备注"]
        lines.append(",".join(headers))
        
        # 数据行
        for field in model_detail['fields']:
            row = [
                field['field_name'],
                field['data_type'],
                field['meaning'],
                "是" if field['required'] == "true" else "否",
                field['default_value'] or "",
                ""
            ]
            lines.append(",".join(row))
        
        return "\n".join(lines) 