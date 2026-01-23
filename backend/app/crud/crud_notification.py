from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.notification import Notification


class CRUDNotification:
    def create(
        self,
        db: Session,
        *,
        user_id: int,
        type: str,
        from_user_id: int,
        blog_id: Optional[int] = None,
        comment_id: Optional[int] = None,
        content: Optional[str] = None
    ) -> Notification:
        """创建通知"""
        db_obj = Notification(
            user_id=user_id,
            type=type,
            from_user_id=from_user_id,
            blog_id=blog_id,
            comment_id=comment_id,
            content=content,
            is_read=False
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def has_recent_notification(
        self,
        db: Session,
        *,
        user_id: int,
        type: str,
        from_user_id: int,
        blog_id: Optional[int] = None,
        comment_id: Optional[int] = None,
        minutes: int = 1
    ) -> bool:
        """检查1分钟内是否已有相同类型的通知（用于频率限制）"""
        since = datetime.utcnow() - timedelta(minutes=minutes)
        query = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.type == type,
            Notification.from_user_id == from_user_id,
            Notification.created_at >= since
        )
        if blog_id:
            query = query.filter(Notification.blog_id == blog_id)
        if comment_id:
            query = query.filter(Notification.comment_id == comment_id)
        return query.first() is not None

    def list_by_user(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Notification]:
        """获取用户的通知列表"""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read == False)
        return (
            query
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_unread(self, db: Session, *, user_id: int) -> int:
        """统计未读通知数"""
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()

    def mark_as_read(self, db: Session, *, notification_id: int, user_id: int) -> bool:
        """标记通知为已读"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        if notification:
            notification.is_read = True
            db.commit()
            return True
        return False

    def mark_all_as_read(self, db: Session, *, user_id: int) -> int:
        """标记用户所有通知为已读"""
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        db.commit()
        return count

    def get(self, db: Session, *, notification_id: int) -> Optional[Notification]:
        """获取单个通知"""
        return db.query(Notification).filter(Notification.id == notification_id).first()


notification = CRUDNotification()
