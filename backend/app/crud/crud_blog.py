from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List, Optional

from app.models.blog import Blog, BlogImage
from app.models.user import User
from app.schemas.blog import BlogCreate, BlogUpdate


class CRUDBlog:
    def create(self, db: Session, *, user_id: int, obj_in: BlogCreate) -> Blog:
        db_obj = Blog(
            user_id=user_id,
            title=obj_in.title,
            content=obj_in.content,
            is_public=obj_in.is_public,
        )
        db.add(db_obj)
        db.flush()  # 获取 blog_id
        
        # 创建图片记录
        if obj_in.image_urls:
            for idx, url in enumerate(obj_in.image_urls[:9]):  # 最多9张
                if url and url.strip():
                    image = BlogImage(
                        blog_id=db_obj.id,
                        image_url=url.strip(),
                        sort_order=idx
                    )
                    db.add(image)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, blog_id: int) -> Optional[Blog]:
        return (
            db.query(Blog)
            .options(joinedload(Blog.images))
            .filter(Blog.id == blog_id)
            .first()
        )

    def list_public(self, db: Session, *, skip: int = 0, limit: int = 20) -> List[Blog]:
        return (
            db.query(Blog)
            .options(joinedload(Blog.images))
            .filter(Blog.is_public == True)
            .order_by(desc(Blog.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_public(self, db: Session) -> int:
        return db.query(Blog).filter(Blog.is_public == True).count()

    def list_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 20) -> List[Blog]:
        return (
            db.query(Blog)
            .options(joinedload(Blog.images))
            .filter(Blog.user_id == user_id)
            .order_by(desc(Blog.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_user(self, db: Session, *, user_id: int) -> int:
        return db.query(Blog).filter(Blog.user_id == user_id).count()

    def update(self, db: Session, *, db_obj: Blog, obj_in: BlogUpdate) -> Blog:
        update_data = obj_in.model_dump(exclude_unset=True, exclude={'image_urls'})
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        # 更新图片
        if 'image_urls' in obj_in.model_dump(exclude_unset=True):
            # 删除旧图片
            db.query(BlogImage).filter(BlogImage.blog_id == db_obj.id).delete()
            # 添加新图片
            if obj_in.image_urls:
                for idx, url in enumerate(obj_in.image_urls[:9]):
                    if url and url.strip():
                        image = BlogImage(
                            blog_id=db_obj.id,
                            image_url=url.strip(),
                            sort_order=idx
                        )
                        db.add(image)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, db_obj: Blog) -> None:
        db.delete(db_obj)
        db.commit()


blog = CRUDBlog()
