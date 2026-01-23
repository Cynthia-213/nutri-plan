from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text, ForeignKey, text, Enum
from sqlalchemy.orm import relationship
from .user import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # 接收通知的用户
    type = Column(Enum('like', 'comment', 'reply'), nullable=False)  # 通知类型
    blog_id = Column(Integer, ForeignKey("blogs.id"), nullable=True, index=True)  # 关联的博客ID
    comment_id = Column(Integer, ForeignKey("blog_comments.id"), nullable=True, index=True)  # 关联的评论ID（如果是评论通知）
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 触发通知的用户
    content = Column(Text, nullable=True)  # 通知内容（如评论内容预览）
    is_read = Column(Boolean, default=False, nullable=False)  # 是否已读
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), index=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="notifications")
    from_user = relationship("User", foreign_keys=[from_user_id])
    blog = relationship("Blog", foreign_keys=[blog_id])
    comment = relationship("BlogComment", foreign_keys=[comment_id])
