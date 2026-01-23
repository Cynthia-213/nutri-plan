import redis
from app.core.config import settings

# 创建Redis连接池
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,  # 自动解码响应为字符串
    socket_connect_timeout=5,
    socket_timeout=5
)

def get_redis() -> redis.Redis:
    """获取Redis客户端实例"""
    return redis_client
