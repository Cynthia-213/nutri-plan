from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import uuid
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)

from app.crud.crud_blog import blog as crud_blog
from app.crud.crud_blog_comment import blog_comment as crud_comment
from app.crud.crud_blog_like import blog_like as crud_like
from app.crud.crud_user import user as crud_user
from app.services.notification_service import notification_service
from app.schemas.blog import (
    BlogCreate,
    BlogUpdate,
    BlogList,
    Blog,
    BlogCommentCreate,
    BlogCommentList,
    BlogComment,
)
from app.models.user import User
from app.core.config import settings
from qcloud_cos import CosConfig, CosS3Client

class BlogService:
    def _enrich_blogs_with_username(self, db: Session, blogs: List, current_user_id: Optional[int] = None) -> List[Blog]:
        """为 Blog 列表添加 username、图片信息和点赞状态"""
        enriched = []
        for blog in blogs:
            user = crud_user.get_user_by_id(db, user_id=blog.user_id)
            # 从关联的图片中提取 URL 列表
            images = [img for img in blog.images] if blog.images else []
            image_urls = [img.image_url for img in sorted(images, key=lambda x: x.sort_order)]
            # 生成兼容的 image_url 字段（逗号分隔）
            image_url_str = ','.join(image_urls) if image_urls else None
            
            # 检查当前用户是否已点赞
            is_liked = False
            if current_user_id:
                is_liked = crud_like.has_liked(db, blog_id=blog.id, user_id=current_user_id)
            
            # 计算评论数
            comments_count = crud_comment.count_by_blog(db, blog_id=blog.id)
            
            blog_dict = {
                "id": blog.id,
                "user_id": blog.user_id,
                "username": user.username if user else None,
                "title": blog.title,
                "content": blog.content,
                "images": images,
                "image_url": image_url_str,  # 兼容字段
                "is_public": blog.is_public,
                "likes_count": blog.likes_count or 0,
                "comments_count": comments_count,
                "is_liked": is_liked,
                "created_at": blog.created_at,
                "updated_at": blog.updated_at,
            }
            enriched.append(Blog(**blog_dict))
        return enriched

    def list_public(self, db: Session, *, skip: int = 0, limit: int = 20, current_user: Optional[User] = None) -> BlogList:
        items = crud_blog.list_public(db, skip=skip, limit=limit)
        total = crud_blog.count_public(db)
        current_user_id = current_user.id if current_user else None
        enriched_items = self._enrich_blogs_with_username(db, items, current_user_id=current_user_id)
        return BlogList(total=total, items=enriched_items)

    def list_my(self, db: Session, *, user: User, skip: int = 0, limit: int = 20) -> BlogList:
        items = crud_blog.list_by_user(db, user_id=user.id, skip=skip, limit=limit)
        total = crud_blog.count_by_user(db, user_id=user.id)
        enriched_items = self._enrich_blogs_with_username(db, items, current_user_id=user.id)
        return BlogList(total=total, items=enriched_items)

    def create(self, db: Session, *, user: User, obj_in: BlogCreate) -> Blog:
        blog = crud_blog.create(db, user_id=user.id, obj_in=obj_in)
        enriched = self._enrich_blogs_with_username(db, [blog], current_user_id=user.id)
        return enriched[0] if enriched else blog

    def get(self, db: Session, *, blog_id: int, current_user: Optional[User] = None) -> Optional[Blog]:
        blog = crud_blog.get(db, blog_id=blog_id)
        if not blog:
            return None
        current_user_id = current_user.id if current_user else None
        enriched = self._enrich_blogs_with_username(db, [blog], current_user_id=current_user_id)
        return enriched[0] if enriched else None

    def update(self, db: Session, *, blog_id: int, user: User, obj_in: BlogUpdate) -> Optional[Blog]:
        db_obj = crud_blog.get(db, blog_id=blog_id)
        if not db_obj or db_obj.user_id != user.id:
            return None
        updated = crud_blog.update(db, db_obj=db_obj, obj_in=obj_in)
        if updated:
            enriched = self._enrich_blogs_with_username(db, [updated], current_user_id=user.id)
            return enriched[0] if enriched else updated
        return None

    def toggle_like(self, db: Session, *, blog_id: int, user: User) -> Optional[Blog]:
        """切换点赞状态：如果已点赞则取消，否则点赞"""
        db_obj = crud_blog.get(db, blog_id=blog_id)
        if not db_obj:
            return None
        
        was_liked = crud_like.has_liked(db, blog_id=blog_id, user_id=user.id)
        
        if was_liked:
            # 取消点赞
            crud_like.delete(db, blog_id=blog_id, user_id=user.id)
        else:
            # 点赞
            crud_like.create(db, blog_id=blog_id, user_id=user.id)
            # 发送点赞通知（只在点赞时发送，取消点赞不发送）
            try:
                notification_service.notify_like(
                    db,
                    blog_id=blog_id,
                    from_user=user
                )
            except Exception as e:
                # 通知失败不应该影响点赞操作
                logging.error(f"Failed to send like notification: {e}")
        
        # 刷新博客对象以获取最新的点赞数
        db.refresh(db_obj)
        # 返回带点赞状态的博客
        enriched = self._enrich_blogs_with_username(db, [db_obj], current_user_id=user.id)
        return enriched[0] if enriched else db_obj

    def create_comment(self, db: Session, *, blog_id: int, user: User, obj_in: BlogCommentCreate) -> BlogComment:
        comment = crud_comment.create(db, blog_id=blog_id, user_id=user.id, obj_in=obj_in)
        # 为评论添加用户名和父评论用户名
        parent_username = None
        if comment.parent_id:
            parent_comment = crud_comment.get(db, comment_id=comment.parent_id)
            if parent_comment:
                parent_user = crud_user.get_user_by_id(db, user_id=parent_comment.user_id)
                parent_username = parent_user.username if parent_user else None
        
        # 发送通知
        try:
            notification_service.notify_comment(
                db,
                blog_id=blog_id,
                comment_id=comment.id,
                from_user=user,
                comment_content=comment.content,
                parent_id=comment.parent_id
            )
        except Exception as e:
            # 通知失败不应该影响评论创建
            logging.error(f"Failed to send comment notification: {e}")
        
        comment_dict = {
            "id": comment.id,
            "blog_id": comment.blog_id,
            "user_id": comment.user_id,
            "username": user.username,
            "content": comment.content,
            "parent_id": comment.parent_id,
            "parent_username": parent_username,
            "created_at": comment.created_at,
        }
        return BlogComment(**comment_dict)

    def list_comments(self, db: Session, *, blog_id: int, skip: int = 0, limit: int = 50) -> BlogCommentList:
        items = crud_comment.list_by_blog(db, blog_id=blog_id, skip=skip, limit=limit)
        total = crud_comment.count_by_blog(db, blog_id=blog_id)
        # 为评论添加用户名和父评论用户名
        enriched_items = []
        for comment in items:
            user = crud_user.get_user_by_id(db, user_id=comment.user_id)
            parent_username = None
            if comment.parent_id:
                parent_comment = crud_comment.get(db, comment_id=comment.parent_id)
                if parent_comment:
                    parent_user = crud_user.get_user_by_id(db, user_id=parent_comment.user_id)
                    parent_username = parent_user.username if parent_user else None
            comment_dict = {
                "id": comment.id,
                "blog_id": comment.blog_id,
                "user_id": comment.user_id,
                "username": user.username if user else None,
                "content": comment.content,
                "parent_id": comment.parent_id,
                "parent_username": parent_username,
                "created_at": comment.created_at,
            }
            enriched_items.append(BlogComment(**comment_dict))
        return BlogCommentList(total=total, items=enriched_items)

    def generate_upload_url(self, *, filename: str, user: User) -> dict:
        """
        生成 COS 预签名上传 URL
        """
        if not all([settings.COS_SECRET_ID, settings.COS_SECRET_KEY, settings.COS_BUCKET, settings.COS_REGION, settings.COS_BASE_URL]):
            raise ValueError("COS config missing")
        if CosConfig is None or CosS3Client is None:
            raise ValueError("qcloud_cos not installed")

        ext = filename.split(".")[-1] if "." in filename else "jpg"
        today = datetime.utcnow().strftime("%Y%m%d")
        key = f"blog/{user.id}/{today}/{uuid.uuid4().hex}.{ext}"

        config = CosConfig(
            Region=settings.COS_REGION,
            SecretId=settings.COS_SECRET_ID,
            SecretKey=settings.COS_SECRET_KEY,
        )
        client = CosS3Client(config)

        upload_url = client.get_presigned_url(
            Method="PUT",
            Bucket=settings.COS_BUCKET,
            Key=key,
            Expired=600,
        )

        file_url = f"{settings.COS_BASE_URL.rstrip('/')}/{key}"
        return {"key": key, "upload_url": upload_url, "file_url": file_url}

    async def upload_file_to_cos(self, *, file, user: User) -> str:
        """
        上传文件到 COS（后端中转）
        """
        if not all([settings.COS_SECRET_ID, settings.COS_SECRET_KEY, settings.COS_BUCKET, settings.COS_REGION, settings.COS_BASE_URL]):
            raise ValueError("COS config missing")

        # 获取文件扩展名
        filename = file.filename or "image.jpg"
        ext = filename.split(".")[-1] if "." in filename else "jpg"
        today = datetime.utcnow().strftime("%Y%m%d")
        key = f"blog/{user.id}/{today}/{uuid.uuid4().hex}.{ext}"

        # 读取文件内容
        file_content = await file.read()

        # 上传到 COS
        config = CosConfig(
            Region=settings.COS_REGION,
            SecretId=settings.COS_SECRET_ID,
            SecretKey=settings.COS_SECRET_KEY,
        )
        client = CosS3Client(config)

        # 根据文件扩展名确定 Content-Type
        content_type_map = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "webp": "image/webp",
        }
        content_type = content_type_map.get(ext.lower(), "image/jpeg")

        # 上传文件
        response = client.put_object(
            Bucket=settings.COS_BUCKET,
            Key=key,
            Body=file_content,
            ContentType=content_type,
        )

        if response.get("ETag"):
            file_url = f"{settings.COS_BASE_URL.rstrip('/')}/{key}"
            return file_url
        else:
            raise ValueError("上传失败")

    def _extract_cos_key_from_url(self, url: str) -> Optional[str]:
        """从COS URL中提取key（用于删除）"""
        if not url or not isinstance(url, str):
            return None
        try:
            # 方法1: 如果URL以COS_BASE_URL开头，直接提取
            if settings.COS_BASE_URL:
                base_url = settings.COS_BASE_URL.rstrip('/')
                if url.startswith(base_url):
                    key = url.replace(base_url, '').lstrip('/')
                    if key:
                        return key
            
            # 方法2: 使用urlparse解析URL，提取path部分
            parsed = urlparse(url)
            path = parsed.path.lstrip('/')
            if path and path.startswith('blog/'):
                return path
            
            # 方法3: 如果URL包含 /blog/，提取之后的部分
            if '/blog/' in url:
                idx = url.find('/blog/')
                if idx >= 0:
                    key = url[idx + 1:]  # 去掉开头的 /
                    # 移除可能的查询参数
                    if '?' in key:
                        key = key.split('?')[0]
                    if key:
                        return key
            
            return None
        except Exception as e:
            logging.warning(f"Failed to extract COS key from URL {url}: {str(e)}")
            return None

    def _delete_images_from_cos(self, image_urls: List[str]) -> None:
        """从COS删除图片（静默失败，不影响主流程）"""
        if not image_urls:
            return
        
        if not all([settings.COS_SECRET_ID, settings.COS_SECRET_KEY, settings.COS_BUCKET, settings.COS_REGION]):
            # COS配置缺失，跳过删除
            return
        
        try:
            config = CosConfig(
                Region=settings.COS_REGION,
                SecretId=settings.COS_SECRET_ID,
                SecretKey=settings.COS_SECRET_KEY,
            )
            client = CosS3Client(config)
            
            # 提取所有有效的key
            keys_to_delete = []
            for url in image_urls:
                key = self._extract_cos_key_from_url(url)
                if key:
                    keys_to_delete.append(key)
            
            # 批量删除
            if keys_to_delete:
                for key in keys_to_delete:
                    try:
                        client.delete_object(
                            Bucket=settings.COS_BUCKET,
                            Key=key,
                        )
                    except Exception as e:
                        # 单个文件删除失败不影响其他文件
                        logging.warning(f"Failed to delete COS object {key}: {str(e)}")
        except Exception as e:
            # COS删除失败不影响博客删除
            logging.warning(f"Failed to delete images from COS: {str(e)}")

    def delete(self, db: Session, *, blog_id: int, user: User) -> bool:
        db_obj = crud_blog.get(db, blog_id=blog_id)
        if not db_obj or db_obj.user_id != user.id:
            return False
        
        # 在删除博客之前，先收集所有图片URL
        image_urls = []
        if db_obj.images:
            image_urls = [img.image_url for img in db_obj.images]
        
        # 删除博客记录（这会触发级联删除blog_images记录）
        crud_blog.delete(db, db_obj=db_obj)
        
        # 删除云上的图片（静默失败，不影响主流程）
        if image_urls:
            self._delete_images_from_cos(image_urls)
        
        return True


blog_service = BlogService()
