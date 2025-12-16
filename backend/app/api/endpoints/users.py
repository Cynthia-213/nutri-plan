from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from app.api import deps
from app.core import security
from app.crud.crud_user import user_crud
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema
from app.schemas.token import Token
from app.db.session import get_db

router = APIRouter()

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """
    用户注册
    - 检查用户名或邮箱是否已存在
    - 创建新用户并存入数据库
    """
    user = user_crud.get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered.",
        )
    user = user_crud.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )
        
    # 创建用户
    user = user_crud.create_user(db, user_in=user_in)
    return user


@router.post("/login/token", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    用户登录以获取访问令牌 (JWT)
    - 使用用户名和密码进行验证
    - 验证成功后返回JWT令牌
    """
    user = user_crud.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    return current_user


@router.put("/me", response_model=UserSchema)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    更新当前登录用户的信息
    - 检查用户名或邮箱是否已存在
    - 更新用户
    """
    if user_in.username:
        existing_user = user_crud.get_user_by_username(db, username=user_in.username)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Username already taken by another user.")

    if user_in.email:
        existing_user = user_crud.get_user_by_email(db, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already registered by another user.")

    user = user_crud.update_user(db, db_user=current_user, user_in=user_in)
    return user