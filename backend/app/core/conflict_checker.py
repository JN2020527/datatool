from typing import List, Dict, Tuple, Optional
from app.core.normalization import normalize_name, validate_name

class ConflictChecker:
    """冲突检测器"""
    
    def __init__(self):
        self.conflict_priority = {
            "naming_invalid": 1,      # 命名非法（最高优先级）
            "root_conflict": 2,        # 词根冲突
            "field_conflict": 3        # 字段冲突（最低优先级）
        }
    
    def check_root_conflicts(
        self, 
        name: str, 
        existing_roots: List[Dict], 
        existing_fields: List[Dict]
    ) -> Tuple[bool, List[str], Optional[str]]:
        """
        检查词根冲突
        
        Args:
            name: 要检查的词根名
            existing_roots: 已存在的词根列表
            existing_fields: 已存在的字段列表
            
        Returns:
            (是否有冲突, 冲突列表, 替代建议)
        """
        conflicts = []
        normalized_name = normalize_name(name)
        
        # 1. 检查命名合法性
        is_valid, error_msg = validate_name(normalized_name, max_length=64)
        if not is_valid:
            return True, [f"命名非法: {error_msg}"], None
        
        # 2. 检查词根冲突
        for root in existing_roots:
            if root.get("normalized_name") == normalized_name:
                conflicts.append(f"词根名冲突: {root.get('name')} (ID: {root.get('id')})")
            elif root.get("name") == name:
                conflicts.append(f"词根名冲突: {root.get('name')} (ID: {root.get('id')})")
        
        # 3. 检查字段冲突
        for field in existing_fields:
            if field.get("normalized_name") == normalized_name:
                conflicts.append(f"字段名冲突: {field.get('field_name')} (ID: {field.get('id')})")
        
        # 4. 生成替代建议
        alternative = None
        if conflicts:
            # 尝试添加后缀
            existing_names = [r.get("normalized_name") for r in existing_roots] + [f.get("normalized_name") for f in existing_fields]
            alternative = self._generate_alternative_name(normalized_name, existing_names)
        
        return len(conflicts) > 0, conflicts, alternative
    
    def check_field_conflicts(
        self, 
        field_name: str, 
        existing_fields: List[Dict]
    ) -> Tuple[bool, List[str], List[str]]:
        """
        检查字段冲突
        
        Args:
            field_name: 要检查的字段名
            existing_fields: 已存在的字段列表
            
        Returns:
            (是否有冲突, 冲突列表, 替代建议列表)
        """
        conflicts = []
        normalized_name = normalize_name(field_name)
        
        # 1. 检查命名合法性
        is_valid, error_msg = validate_name(normalized_name, max_length=128)
        if not is_valid:
            return True, [f"命名非法: {error_msg}"], []
        
        # 2. 检查字段冲突
        for field in existing_fields:
            if field.get("normalized_name") == normalized_name:
                conflicts.append(f"字段名冲突: {field.get('field_name')} (ID: {field.get('id')})")
        
        # 3. 生成替代建议
        alternatives = []
        if conflicts:
            existing_names = [f.get("normalized_name") for f in existing_fields]
            alternatives = self._generate_field_alternatives(normalized_name, existing_names)
        
        return len(conflicts) > 0, conflicts, alternatives
    
    def _generate_alternative_name(self, base_name: str, existing_names: List[str]) -> str:
        """生成词根替代名称"""
        import time
        
        # 尝试添加数字后缀
        for i in range(1, 100):
            alternative = f"{base_name}_{i}"
            if alternative not in existing_names:
                return alternative
        
        # 如果还是冲突，使用时间戳
        timestamp = int(time.time() % 10000)
        return f"{base_name}_{timestamp}"
    
    def _generate_field_alternatives(self, base_name: str, existing_names: List[str]) -> List[str]:
        """生成字段替代名称列表"""
        alternatives = []
        
        # 常用后缀
        suffixes = ["_v2", "_daily", "_monthly", "_amount", "_cnt", "_ts", "_id"]
        
        for suffix in suffixes:
            alternative = base_name + suffix
            if alternative not in existing_names:
                alternatives.append(alternative)
                if len(alternatives) >= 3:  # 最多返回3个建议
                    break
        
        # 如果后缀不够，添加数字
        if len(alternatives) < 3:
            for i in range(1, 10):
                alternative = f"{base_name}_{i}"
                if alternative not in existing_names and alternative not in alternatives:
                    alternatives.append(alternative)
                    if len(alternatives) >= 3:
                        break
        
        return alternatives
    
    def get_conflict_priority(self, conflict_type: str) -> int:
        """获取冲突优先级"""
        return self.conflict_priority.get(conflict_type, 999)
    
    def sort_conflicts_by_priority(self, conflicts: List[Dict]) -> List[Dict]:
        """按优先级排序冲突"""
        return sorted(conflicts, key=lambda x: self.get_conflict_priority(x.get("type", ""))) 