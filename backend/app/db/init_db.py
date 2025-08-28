#!/usr/bin/env python3
"""
数据库初始化脚本
支持SQLite和PostgreSQL数据库
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.database import init_database, check_database_health
from app.core.config import settings
import logging

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    try:
        logger.info("开始初始化数据库...")
        logger.info(f"数据库类型: {settings.DATABASE_TYPE}")
        logger.info(f"数据库URL: {settings.get_database_url()}")
        
        # 检查数据库连接
        if not check_database_health():
            logger.error("数据库连接失败，请检查配置")
            sys.exit(1)
        
        # 初始化数据库
        init_database()
        
        logger.info("数据库初始化完成！")
        
        # 显示数据库信息
        if settings.DATABASE_TYPE.lower() == "postgresql":
            logger.info(f"PostgreSQL数据库 '{settings.POSTGRES_DB}' 初始化成功")
            logger.info(f"连接池配置: pool_size={settings.POSTGRES_POOL_SIZE}, max_overflow={settings.POSTGRES_MAX_OVERFLOW}")
        else:
            logger.info(f"SQLite数据库 '{settings.SQLITE_DB_PATH}' 初始化成功")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 