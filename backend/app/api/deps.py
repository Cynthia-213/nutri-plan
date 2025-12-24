import logging
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core import security
from app.db.session import get_db
from app.models.user import User
from app.crud.crud_user import user as crud_user
from app.schemas.token import TokenData

# 创建一个 OAuth2PasswordBearer 实例
# tokenUrl 指向我们将要创建的登录端点
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/api/users/login/token"
)

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    """
    一个依赖项，用于：
    1. 从请求中提取JWT令牌。
    2. 解码令牌。
    3. 从数据库中获取用户。
    4. 返回用户对象。
    如果令牌无效或用户不存在，则会引发HTTPException。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 解码令牌
    payload = security.decode_access_token(token)
    if payload is None:
        logging.debug("Token payload is None")
        raise credentials_exception
        
    username: str = payload.get("sub")
    if username is None:
        logging.debug("Username not found in token payload")
        raise credentials_exception
        
    token_data = TokenData(username=username)
    
    # 从数据库获取用户
    user = crud_user.get_user_by_username(db, username=token_data.username)
    if user is None:
        logging.debug(f"User not found: {token_data.username}")
        raise credentials_exception
        
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    一个依赖项，用于检查当前用户是否处于活动状态。
    （在这个项目中我们没有is_active字段，但这是一个很好的实践，可以保留以备将来扩展）
    """
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user