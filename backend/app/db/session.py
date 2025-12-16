from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 创建数据库引擎
# connect_args 是特定于 aqlite 的，对于 MySQL/PyMySQL，通常不需要
# pool_pre_ping=True 会在每次从池中获取连接时检查其有效性
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True
)

# 创建一个SessionLocal类，这个类的实例将是实际的数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建一个依赖项，用于在请求处理期间获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
