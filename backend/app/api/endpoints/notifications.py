"""
通知API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Any

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.crud.crud_notification import notification as crud_notification
from app.crud.crud_user import user as crud_user
from app.schemas.notification import NotificationList, Notification

router = APIRouter()


@router.get("/", response_model=NotificationList)
def list_notifications(
    *,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    获取当前用户的通知列表
    """
    items = crud_notification.list_by_user(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only
    )
    
    # 为通知添加from_username
    enriched_items = []
    for item in items:
        from_user = crud_user.get_user_by_id(db, user_id=item.from_user_id)
        item_dict = {
            "id": item.id,
            "user_id": item.user_id,
            "type": item.type,
            "blog_id": item.blog_id,
            "comment_id": item.comment_id,
            "from_user_id": item.from_user_id,
            "from_username": from_user.username if from_user else None,
            "content": item.content,
            "is_read": item.is_read,
            "created_at": item.created_at,
        }
        enriched_items.append(Notification(**item_dict))
    
    # 计算总数（需要查询所有符合条件的记录）
    from app.models.notification import Notification as NotificationModel
    total_query = db.query(NotificationModel).filter(NotificationModel.user_id == current_user.id)
    if unread_only:
        total_query = total_query.filter(NotificationModel.is_read == False)
    total = total_query.count()
    unread_count = crud_notification.count_unread(db, user_id=current_user.id)
    
    return NotificationList(
        total=total,
        unread_count=unread_count,
        items=enriched_items
    )


@router.get("/unread-count", response_model=dict)
def get_unread_count(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    获取未读通知数
    """
    count = crud_notification.count_unread(db, user_id=current_user.id)
    return {"unread_count": count}


@router.patch("/{notification_id}/read", response_model=Notification)
def mark_as_read(
    *,
    db: Session = Depends(get_db),
    notification_id: int,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    标记单个通知为已读
    """
    success = crud_notification.mark_as_read(db, notification_id=notification_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found.")
    
    # 返回更新后的通知
    notification = crud_notification.get(db, notification_id=notification_id)
    if notification and notification.user_id == current_user.id:
        from_user = crud_user.get_user_by_id(db, user_id=notification.from_user_id)
        return Notification(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            blog_id=notification.blog_id,
            comment_id=notification.comment_id,
            from_user_id=notification.from_user_id,
            from_username=from_user.username if from_user else None,
            content=notification.content,
            is_read=notification.is_read,
            created_at=notification.created_at,
        )
    raise HTTPException(status_code=404, detail="Notification not found.")


@router.post("/mark-all-read", response_model=dict)
def mark_all_as_read(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    标记所有通知为已读
    """
    count = crud_notification.mark_all_as_read(db, user_id=current_user.id)
    return {"marked_count": count}
