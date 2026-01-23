from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum


class NotificationType(str, Enum):
    like = 'like'
    comment = 'comment'
    reply = 'reply'


class NotificationBase(BaseModel):
    type: NotificationType
    blog_id: Optional[int] = None
    comment_id: Optional[int] = None
    from_user_id: int
    content: Optional[str] = None


class Notification(NotificationBase):
    id: int
    user_id: int
    from_username: Optional[str] = None  # 触发通知的用户名
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationList(BaseModel):
    total: int
    unread_count: int
    items: List[Notification]


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
