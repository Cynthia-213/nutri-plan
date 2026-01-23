"""
通知服务 - 处理点赞和评论通知
"""
from sqlalchemy.orm import Session
from typing import Optional
from app.crud.crud_notification import notification as crud_notification
from app.crud.crud_blog import blog as crud_blog
from app.crud.crud_blog_comment import blog_comment as crud_comment
from app.models.user import User


class NotificationService:
    """
    通知规则：
    1. 主评论：仅通知帖子发布者
    2. 主评论的子评论：仅通知主评论的发布者（除非主评论人就是帖主）
    3. 针对子评论的回复：通知被回复的子评论发布者 + 主评论发布者（但不通知帖子发布者）
    4. 点赞帖子：通知帖子发布者
    5. 频率限制：同一用户在1分钟内对同一目标多次操作，只发送一次通知
    """
    
    def notify_comment(
        self,
        db: Session,
        *,
        blog_id: int,
        comment_id: int,
        from_user: User,
        comment_content: str,
        parent_id: Optional[int] = None
    ):
        """发送评论通知"""
        blog = crud_blog.get(db, blog_id=blog_id)
        if not blog:
            return
        
        blog_owner_id = blog.user_id
        
        # 获取评论信息
        comment = crud_comment.get(db, comment_id=comment_id)
        if not comment:
            return
        
        # 截取评论内容预览（前50字符）
        content_preview = comment_content[:50] + ("..." if len(comment_content) > 50 else "")
        
        if parent_id is None:
            # 主评论：仅通知帖子发布者
            if blog_owner_id != from_user.id:
                # 检查频率限制
                if not crud_notification.has_recent_notification(
                    db,
                    user_id=blog_owner_id,
                    type='comment',
                    from_user_id=from_user.id,
                    blog_id=blog_id,
                    minutes=1
                ):
                    crud_notification.create(
                        db,
                        user_id=blog_owner_id,
                        type='comment',
                        from_user_id=from_user.id,
                        blog_id=blog_id,
                        comment_id=comment_id,
                        content=content_preview
                    )
        else:
            # 子评论：需要判断是回复主评论还是回复子评论
            parent_comment = crud_comment.get(db, comment_id=parent_id)
            if not parent_comment:
                return
            
            parent_commenter_id = parent_comment.user_id
            
            # 检查父评论是否是主评论（parent_id为None）
            if parent_comment.parent_id is None:
                # 回复主评论：仅通知主评论的发布者（除非主评论人就是帖主）
                if parent_commenter_id != blog_owner_id and parent_commenter_id != from_user.id:
                    if not crud_notification.has_recent_notification(
                        db,
                        user_id=parent_commenter_id,
                        type='reply',
                        from_user_id=from_user.id,
                        blog_id=blog_id,
                        comment_id=parent_id,
                        minutes=1
                    ):
                        crud_notification.create(
                            db,
                            user_id=parent_commenter_id,
                            type='reply',
                            from_user_id=from_user.id,
                            blog_id=blog_id,
                            comment_id=comment_id,
                            content=content_preview
                        )
            else:
                # 回复子评论（盖楼）：通知被回复的子评论发布者 + 主评论发布者
                # 1. 通知被回复的子评论发布者
                if parent_commenter_id != from_user.id:
                    if not crud_notification.has_recent_notification(
                        db,
                        user_id=parent_commenter_id,
                        type='reply',
                        from_user_id=from_user.id,
                        blog_id=blog_id,
                        comment_id=parent_id,
                        minutes=1
                    ):
                        crud_notification.create(
                            db,
                            user_id=parent_commenter_id,
                            type='reply',
                            from_user_id=from_user.id,
                            blog_id=blog_id,
                            comment_id=comment_id,
                            content=content_preview
                        )
                
                # 2. 找到主评论发布者（向上查找直到parent_id为None）
                main_comment = parent_comment
                while main_comment and main_comment.parent_id is not None:
                    temp_comment = crud_comment.get(db, comment_id=main_comment.parent_id)
                    if not temp_comment:
                        break
                    main_comment = temp_comment
                
                main_commenter_id = main_comment.user_id if main_comment else None
                
                # 通知主评论发布者（如果主评论人不是帖主，且不是被回复的人，且不是当前用户）
                if (main_commenter_id and 
                    main_commenter_id != blog_owner_id and 
                    main_commenter_id != parent_commenter_id and 
                    main_commenter_id != from_user.id):
                    if not crud_notification.has_recent_notification(
                        db,
                        user_id=main_commenter_id,
                        type='reply',
                        from_user_id=from_user.id,
                        blog_id=blog_id,
                        comment_id=main_comment.id if main_comment else None,
                        minutes=1
                    ):
                        crud_notification.create(
                            db,
                            user_id=main_commenter_id,
                            type='reply',
                            from_user_id=from_user.id,
                            blog_id=blog_id,
                            comment_id=comment_id,
                            content=content_preview
                        )
    
    def notify_like(
        self,
        db: Session,
        *,
        blog_id: int,
        from_user: User
    ):
        """发送点赞通知"""
        blog = crud_blog.get(db, blog_id=blog_id)
        if not blog:
            return
        
        blog_owner_id = blog.user_id
        
        # 不通知自己
        if blog_owner_id == from_user.id:
            return
        
        # 检查频率限制
        if not crud_notification.has_recent_notification(
            db,
            user_id=blog_owner_id,
            type='like',
            from_user_id=from_user.id,
            blog_id=blog_id,
            minutes=1
        ):
            crud_notification.create(
                db,
                user_id=blog_owner_id,
                type='like',
                from_user_id=from_user.id,
                blog_id=blog_id,
                content=None
            )


notification_service = NotificationService()
