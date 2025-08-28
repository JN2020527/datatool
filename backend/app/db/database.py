from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.core.config import settings
import logging

# 配置日志
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

def create_database_engine():
    """创建数据库引擎"""
    database_url = settings.get_database_url()
    database_config = settings.get_database_config()
    
    logger.info(f"连接数据库: {settings.DATABASE_TYPE}")
    logger.info(f"数据库URL: {database_url}")
    
    if settings.DATABASE_TYPE.lower() == "postgresql":
        # PostgreSQL配置
        engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=database_config["pool_size"],
            max_overflow=database_config["max_overflow"],
            pool_timeout=database_config["pool_timeout"],
            pool_recycle=database_config["pool_recycle"],
            echo=database_config["echo"]
        )
        logger.info(f"PostgreSQL连接池配置: pool_size={database_config['pool_size']}, max_overflow={database_config['max_overflow']}")
    else:
        # SQLite配置
        engine = create_engine(
            database_url,
            echo=database_config["echo"],
            connect_args=database_config["connect_args"]
        )
        logger.info("使用SQLite数据库")
    
    return engine

# 创建数据库引擎
engine = create_database_engine()

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """初始化数据库"""
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
        
        # 如果是PostgreSQL，创建索引
        if settings.DATABASE_TYPE.lower() == "postgresql":
            create_postgresql_indexes()
            
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

def create_postgresql_indexes():
    """创建PostgreSQL索引"""
    try:
        with engine.connect() as conn:
            # 创建词根索引
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_roots_normalized_name 
                ON roots (normalized_name);
            """)
            
            # 创建字段索引
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fields_normalized_name 
                ON fields (normalized_name);
            """)
            
            # 创建模型索引
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_models_model_name 
                ON models (model_name);
            """)
            
            # 创建关联表索引
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_model_fields_model_id 
                ON model_fields (model_id);
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_model_fields_field_id 
                ON model_fields (field_id);
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_lineages_field_id 
                ON lineages (field_id);
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_lineages_model_id 
                ON lineages (model_id);
            """)
            
            conn.commit()
            logger.info("PostgreSQL索引创建成功")
            
    except Exception as e:
        logger.warning(f"PostgreSQL索引创建失败: {e}")

def close_database():
    """关闭数据库连接"""
    try:
        engine.dispose()
        logger.info("数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接失败: {e}")

# 数据库健康检查
def check_database_health():
    """检查数据库健康状态"""
    try:
        with engine.connect() as conn:
            if settings.DATABASE_TYPE.lower() == "postgresql":
                result = conn.execute("SELECT 1")
            else:
                # SQLite使用text()函数包装SQL语句
                from sqlalchemy import text
                result = conn.execute(text("SELECT 1"))
            result.fetchone()
            return True
    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        return False 