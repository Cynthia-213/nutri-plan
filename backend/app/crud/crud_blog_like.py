from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional

from app.models.blog import BlogLike, Blog


class CRUDBlogLike:
    def has_liked(self, db: Session, *, blog_id: int, user_id: int) -> bool:
        """检查用户是否已点赞"""
        return (
            db.query(BlogLike)
            .filter(and_(BlogLike.blog_id == blog_id, BlogLike.user_id == user_id))
            .first()
            is not None
        )

    def create(self, db: Session, *, blog_id: int, user_id: int) -> BlogLike:
        """创建点赞记录"""
        db_obj = BlogLike(blog_id=blog_id, user_id=user_id)
        db.add(db_obj)
        
        # 更新博客的点赞数
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        if blog:
            blog.likes_count = (blog.likes_count or 0) + 1
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, blog_id: int, user_id: int) -> bool:
        """删除点赞记录（取消点赞）"""
        like_obj = (
            db.query(BlogLike)
            .filter(and_(BlogLike.blog_id == blog_id, BlogLike.user_id == user_id))
            .first()
        )
        if not like_obj:
            return False
        
        # 更新博客的点赞数
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        if blog and blog.likes_count > 0:
            blog.likes_count = blog.likes_count - 1
        
        db.delete(like_obj)
        db.commit()
        return True


blog_like = CRUDBlogLike()
