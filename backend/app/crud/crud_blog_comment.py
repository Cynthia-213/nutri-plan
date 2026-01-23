from sqlalchemy.orm import Session
from sqlalchemy import asc
from typing import List, Optional

from app.models.blog import BlogComment
from app.schemas.blog import BlogCommentCreate


class CRUDBlogComment:
    def create(self, db: Session, *, blog_id: int, user_id: int, obj_in: BlogCommentCreate) -> BlogComment:
        db_obj = BlogComment(
            blog_id=blog_id,
            user_id=user_id,
            content=obj_in.content,
            parent_id=obj_in.parent_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def list_by_blog(self, db: Session, *, blog_id: int, skip: int = 0, limit: int = 50) -> List[BlogComment]:
        return (
            db.query(BlogComment)
            .filter(BlogComment.blog_id == blog_id)
            .order_by(asc(BlogComment.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_blog(self, db: Session, *, blog_id: int) -> int:
        return db.query(BlogComment).filter(BlogComment.blog_id == blog_id).count()

    def get(self, db: Session, *, comment_id: int) -> Optional[BlogComment]:
        return db.query(BlogComment).filter(BlogComment.id == comment_id).first()


blog_comment = CRUDBlogComment()
