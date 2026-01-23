from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from app.api import deps
from app.core import security
from app.crud.crud_user import user
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema, PasswordChange
from app.schemas.token import Token
from app.db.session import get_db
from app.services.ranking_service import ranking_service

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
    cur_user = user.get_user_by_username(db, username=user_in.username)
    if cur_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered.",
        )
    cur_user = user.get_user_by_email(db, email=user_in.email)
    if cur_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )
        
    # 创建用户
    cur_user = user.create_user(db, user_in=user_in)
    return cur_user


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
    print(form_data.username, form_data.password)
    cur_user = user.get_user_by_username(db, username=form_data.username)
    if not cur_user or not security.verify_password(form_data.password, cur_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(data={"sub": cur_user.username})
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
    - 如果身份改变，更新排行榜
    """
    if user_in.username:
        existing_user = user.get_user_by_username(db, username=user_in.username)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Username already taken by another user.")

    if user_in.email:
        existing_user = user.get_user_by_email(db, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already registered by another user.")

    # 检查身份是否改变
    old_identity = current_user.identity if hasattr(current_user, 'identity') else 'office_worker'
    new_identity = user_in.identity if user_in.identity else old_identity
    
    cur_user = user.update_user(db, db_user=current_user, user_in=user_in)
    
    # 如果身份改变，更新排行榜
    if user_in.identity and old_identity != new_identity:
        try:
            ranking_service.update_user_identity(
                user_id=cur_user.id,
                old_identity=old_identity,
                new_identity=new_identity
            )
        except Exception as e:
            # 排行榜更新失败不应该影响用户信息更新
            print(f"Failed to update ranking for identity change: {e}")
    
    return cur_user


@router.post("/change-password", response_model=dict)
def change_password(
    *,
    db: Session = Depends(get_db),
    password_data: PasswordChange,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    修改密码
    - 验证旧密码
    - 更新为新密码
    """
    # 验证旧密码
    if not security.verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码不正确"
        )
    
    # 更新密码
    new_hashed_password = security.get_password_hash(password_data.new_password)
    current_user.hashed_password = new_hashed_password
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return {"message": "密码修改成功"}


@router.post("/logout")
def logout(
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    用户登出
    - 在基于JWT的认证中，服务器端通常不处理登出。
    - 客户端应负责删除本地存储的令牌。
    - 此端点仅用于确认登出操作。
    """
    return {"message": "Logout successful"}