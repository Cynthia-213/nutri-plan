from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.core.config import settings

# 创建一个 CryptContext 实例，用于密码的哈希和验证
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 验证明文密码是否与哈希后的密码匹配
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    # 对明文密码进行哈希处理
    return pwd_context.hash(password)


# JSON Web Token

ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌。
    
    :param data: 要编码到令牌中的数据 (通常是用户ID或用户名)。
    :param expires_delta: 令牌的过期时间。如果未提供，将使用配置中的默认值。
    :return: 编码后的JWT令牌字符串。
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    解码JWT访问令牌。
    
    :param token: JWT令牌字符串。
    :return: 如果令牌有效且未过期，则返回解码后的数据；否则返回None。
    """
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token
    except JWTError:
        return None
