import os
from pydantic_settings import BaseSettings
from typing import Optional

# 使用os.path.join来构建.env文件的路径，确保跨平台兼容性
# .env 文件应该位于 backend/ 目录下，与 app/ 目录同级
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')

class Settings(BaseSettings):
    # Database settings
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_SERVER: str
    MYSQL_PORT: str
    MYSQL_DB: str
    
    # SQLAlchemy Database URL
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    # JWT settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # AI settings
    GEMINI_API_KEY: Optional[str] = None
    GLM_KEY: Optional[str] = None
    ZHIPU_API_KEY: Optional[str] = None

    class Config:
        env_file = env_path
        env_file_encoding = 'utf-8'

# 创建一个全局可用的Settings实例
settings = Settings()
