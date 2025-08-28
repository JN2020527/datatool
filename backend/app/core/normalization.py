import re
import unicodedata
from typing import Optional

def normalize_name(name: str) -> str:
    """
    规范化名称：转换为snake_case标准格式
    
    Args:
        name: 输入的名称
        
    Returns:
        规范化后的名称
    """
    if not name:
        return ""
    
    # 1. 全角转半角
    name = unicodedata.normalize('NFKC', name)
    
    # 2. 转换为小写
    name = name.lower()
    
    # 3. 处理空白字符
    name = re.sub(r'\s+', '_', name.strip())
    
    # 4. 处理特殊字符，只保留字母、数字、下划线
    name = re.sub(r'[^a-z0-9_]', '', name)
    
    # 5. 处理连续下划线
    name = re.sub(r'_+', '_', name)
    
    # 6. 去除首尾下划线
    name = name.strip('_')
    
    return name

def validate_name(name: str, max_length: int = 64) -> tuple[bool, Optional[str]]:
    """
    验证名称是否符合规范
    
    Args:
        name: 要验证的名称
        max_length: 最大长度限制
        
    Returns:
        (是否有效, 错误信息)
    """
    if not name:
        return False, "名称不能为空"
    
    if len(name) > max_length:
        return False, f"名称长度不能超过{max_length}个字符"
    
    # 检查是否以字母开头
    if not re.match(r'^[a-z]', name):
        return False, "名称必须以小写字母开头"
    
    # 检查是否只包含合法字符
    if not re.match(r'^[a-z0-9_]+$', name):
        return False, "名称只能包含小写字母、数字和下划线"
    
    # 检查连续下划线
    if '__' in name:
        return False, "名称不能包含连续下划线"
    
    # 检查首尾下划线
    if name.startswith('_') or name.endswith('_'):
        return False, "名称不能以下划线开头或结尾"
    
    return True, None

def generate_normalized_name(base_name: str, existing_names: list[str], max_length: int = 64) -> str:
    """
    生成规范化的名称，如果冲突则自动添加后缀
    
    Args:
        base_name: 基础名称
        existing_names: 已存在的名称列表
        max_length: 最大长度限制
        
    Returns:
        可用的规范化名称
    """
    normalized = normalize_name(base_name)
    
    if not normalized:
        normalized = "unnamed"
    
    # 如果名称可用，直接返回
    if normalized not in existing_names:
        return normalized
    
    # 生成带后缀的名称
    counter = 1
    while counter < 1000:  # 防止无限循环
        suffix = f"_{counter}"
        new_name = normalized + suffix
        
        # 检查长度限制
        if len(new_name) <= max_length and new_name not in existing_names:
            return new_name
        
        counter += 1
    
    # 如果还是冲突，使用时间戳后缀
    import time
    timestamp = int(time.time() % 10000)
    return f"{normalized}_{timestamp}"

def is_atomic_root(name: str) -> bool:
    """
    判断是否为原子词根（不含下划线）
    
    Args:
        name: 词根名称
        
    Returns:
        是否为原子词根
    """
    return '_' not in name

def is_root_phrase(name: str) -> bool:
    """
    判断是否为词根短语（包含下划线）
    
    Args:
        name: 词根名称
        
    Returns:
        是否为词根短语
    """
    return '_' in name 