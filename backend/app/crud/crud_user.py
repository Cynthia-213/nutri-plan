from sqlalchemy.orm import Session
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

class CRUDUser:
    def get_user_by_id(self, db: Session, *, user_id: int) -> Optional[User]:
        """通过ID获取用户"""
        return db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """通过电子邮箱获取用户"""
        return db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        return db.query(User).filter(User.username == username).first()

    def create_user(self, db: Session, *, user_in: UserCreate) -> User:
        """创建新用户"""
        # 对密码进行哈希处理
        hashed_password = get_password_hash(user_in.password)
        # 将Pydantic模型转换为字典
        user_data = user_in.model_dump()
        # 从字典中移除原始密码，因为它不应该直接存储
        del user_data['password']
        
        # 创建数据库模型实例
        db_user = User(
            **user_data,
            hashed_password=hashed_password
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def update_user(self, db: Session, *, db_user: User, user_in: UserUpdate) -> User:
        """更新用户信息"""
        # 将Pydantic模型转换为字典，只包含已设置的字段
        update_data = user_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
            
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

# 创建一个CRUDUser的实例，以便在其他地方导入和使用
user_crud = CRUDUser()
