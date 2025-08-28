from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基本信息
    APP_NAME: str = "Data Dict Tool"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    DATABASE_TYPE: str = "sqlite"  # sqlite 或 postgresql
    DATABASE_URL: str = "sqlite:///./datatool.db"
    DATABASE_ECHO: bool = False
    
    # PostgreSQL 特定配置
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "datatool"
    POSTGRES_POOL_SIZE: int = 10
    POSTGRES_MAX_OVERFLOW: int = 20
    POSTGRES_POOL_TIMEOUT: int = 30
    POSTGRES_POOL_RECYCLE: int = 3600
    
    # SQLite 特定配置
    SQLITE_DB_PATH: str = "./datatool.db"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        if self.DATABASE_TYPE.lower() == "postgresql":
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        else:
            # 默认使用SQLite
            return f"sqlite:///{self.SQLITE_DB_PATH}"
    
    def get_database_config(self) -> dict:
        """获取数据库配置参数"""
        if self.DATABASE_TYPE.lower() == "postgresql":
            return {
                "pool_size": self.POSTGRES_POOL_SIZE,
                "max_overflow": self.POSTGRES_MAX_OVERFLOW,
                "pool_timeout": self.POSTGRES_POOL_TIMEOUT,
                "pool_recycle": self.POSTGRES_POOL_RECYCLE,
                "echo": self.DATABASE_ECHO
            }
        else:
            # SQLite配置
            return {
                "echo": self.DATABASE_ECHO,
                "connect_args": {"check_same_thread": False}
            }

# 创建全局配置实例
settings = Settings()

# 环境变量覆盖
def load_env_config():
    """加载环境变量配置"""
    # 数据库类型
    if os.getenv("DATABASE_TYPE"):
        settings.DATABASE_TYPE = os.getenv("DATABASE_TYPE")
    
    # PostgreSQL配置
    if os.getenv("POSTGRES_HOST"):
        settings.POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    if os.getenv("POSTGRES_PORT"):
        settings.POSTGRES_PORT = int(os.getenv("POSTGRES_PORT"))
    if os.getenv("POSTGRES_USER"):
        settings.POSTGRES_USER = os.getenv("POSTGRES_USER")
    if os.getenv("POSTGRES_PASSWORD"):
        settings.POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    if os.getenv("POSTGRES_DB"):
        settings.POSTGRES_DB = os.getenv("POSTGRES_DB")
    
    # 连接池配置
    if os.getenv("POSTGRES_POOL_SIZE"):
        settings.POSTGRES_POOL_SIZE = int(os.getenv("POSTGRES_POOL_SIZE"))
    if os.getenv("POSTGRES_MAX_OVERFLOW"):
        settings.POSTGRES_MAX_OVERFLOW = int(os.getenv("POSTGRES_MAX_OVERFLOW"))
    
    # 调试模式
    if os.getenv("DEBUG"):
        settings.DEBUG = os.getenv("DEBUG").lower() in ("true", "1", "yes")
    
    # 日志级别
    if os.getenv("LOG_LEVEL"):
        settings.LOG_LEVEL = os.getenv("LOG_LEVEL")

# 加载环境配置
load_env_config() 