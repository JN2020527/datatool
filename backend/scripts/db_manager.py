#!/usr/bin/env python3
"""
数据库管理脚本
提供数据库的初始化、备份、恢复、状态检查等功能
"""

import sys
import os
import argparse
import sqlite3
import shutil
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import init_database, check_database_health, close_database
from app.core.config import settings
import logging

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

def check_sqlite_backup():
    """检查SQLite备份文件"""
    backup_dir = "./backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backup_dir}/datatool_{timestamp}.db"
    
    return backup_file

def backup_sqlite():
    """备份SQLite数据库"""
    if settings.DATABASE_TYPE.lower() != "sqlite":
        logger.warning("只有SQLite数据库支持备份功能")
        return False
    
    try:
        source_db = settings.SQLITE_DB_PATH
        if not os.path.exists(source_db):
            logger.error(f"源数据库文件不存在: {source_db}")
            return False
        
        backup_file = check_sqlite_backup()
        shutil.copy2(source_db, backup_file)
        logger.info(f"SQLite数据库备份成功: {backup_file}")
        return True
        
    except Exception as e:
        logger.error(f"SQLite数据库备份失败: {e}")
        return False

def restore_sqlite(backup_file):
    """恢复SQLite数据库"""
    if settings.DATABASE_TYPE.lower() != "sqlite":
        logger.warning("只有SQLite数据库支持恢复功能")
        return False
    
    try:
        if not os.path.exists(backup_file):
            logger.error(f"备份文件不存在: {backup_file}")
            return False
        
        target_db = settings.SQLITE_DB_PATH
        
        # 先备份当前数据库
        current_backup = check_sqlite_backup()
        if os.path.exists(target_db):
            shutil.copy2(target_db, current_backup)
            logger.info(f"当前数据库已备份: {current_backup}")
        
        # 恢复备份
        shutil.copy2(backup_file, target_db)
        logger.info(f"SQLite数据库恢复成功: {backup_file}")
        return True
        
    except Exception as e:
        logger.error(f"SQLite数据库恢复失败: {e}")
        return False

def list_backups():
    """列出所有备份文件"""
    backup_dir = "./backups"
    if not os.path.exists(backup_dir):
        logger.info("备份目录不存在")
        return
    
    backup_files = []
    for file in os.listdir(backup_dir):
        if file.endswith('.db') and file.startswith('datatool_'):
            file_path = os.path.join(backup_dir, file)
            file_size = os.path.getsize(file_path)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            backup_files.append((file, file_size, file_time))
    
    if not backup_files:
        logger.info("没有找到备份文件")
        return
    
    logger.info("可用备份文件:")
    for file, size, time in sorted(backup_files, key=lambda x: x[2], reverse=True):
        size_mb = size / (1024 * 1024)
        logger.info(f"  {file} - {size_mb:.2f}MB - {time.strftime('%Y-%m-%d %H:%M:%S')}")

def check_database_status():
    """检查数据库状态"""
    logger.info("=== 数据库状态检查 ===")
    logger.info(f"数据库类型: {settings.DATABASE_TYPE}")
    logger.info(f"数据库URL: {settings.get_database_url()}")
    
    if settings.DATABASE_TYPE.lower() == "postgresql":
        logger.info(f"PostgreSQL主机: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
        logger.info(f"数据库名: {settings.POSTGRES_DB}")
        logger.info(f"连接池配置: pool_size={settings.POSTGRES_POOL_SIZE}, max_overflow={settings.POSTGRES_MAX_OVERFLOW}")
    else:
        logger.info(f"SQLite数据库路径: {settings.SQLITE_DB_PATH}")
        if os.path.exists(settings.SQLITE_DB_PATH):
            file_size = os.path.getsize(settings.SQLITE_DB_PATH)
            size_mb = file_size / (1024 * 1024)
            logger.info(f"数据库文件大小: {size_mb:.2f}MB")
        else:
            logger.warning("SQLite数据库文件不存在")
    
    # 检查连接
    if check_database_health():
        logger.info("✓ 数据库连接正常")
    else:
        logger.error("✗ 数据库连接失败")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="数据库管理工具")
    parser.add_argument("action", choices=[
        "init", "backup", "restore", "status", "list-backups"
    ], help="要执行的操作")
    parser.add_argument("--backup-file", help="恢复时指定的备份文件路径")
    parser.add_argument("--force", action="store_true", help="强制执行操作")
    
    args = parser.parse_args()
    
    try:
        if args.action == "init":
            logger.info("初始化数据库...")
            init_database()
            logger.info("数据库初始化完成")
            
        elif args.action == "backup":
            if backup_sqlite():
                logger.info("数据库备份完成")
            else:
                sys.exit(1)
                
        elif args.action == "restore":
            if not args.backup_file:
                logger.error("恢复操作需要指定备份文件路径 (--backup-file)")
                sys.exit(1)
            
            if not args.force:
                logger.warning("恢复操作将覆盖当前数据库，使用 --force 确认执行")
                sys.exit(1)
            
            if restore_sqlite(args.backup_file):
                logger.info("数据库恢复完成")
            else:
                sys.exit(1)
                
        elif args.action == "status":
            check_database_status()
            
        elif args.action == "list-backups":
            list_backups()
            
    except KeyboardInterrupt:
        logger.info("操作被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"操作失败: {e}")
        sys.exit(1)
    finally:
        close_database()

if __name__ == "__main__":
    main() 