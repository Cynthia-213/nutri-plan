from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class BlogImageSchema(BaseModel):
    id: int
    blog_id: int
    image_url: str
    sort_order: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BlogBase(BaseModel):
    title: str
    content: str
    is_public: bool = True


class BlogCreate(BlogBase):
    image_urls: Optional[List[str]] = None  # 图片URL列表，最多9张


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_urls: Optional[List[str]] = None
    is_public: Optional[bool] = None


class Blog(BlogBase):
    id: int
    user_id: int
    username: Optional[str] = None
    likes_count: int
    comments_count: Optional[int] = 0  # 评论数
    is_liked: Optional[bool] = False  # 当前用户是否已点赞
    images: List[BlogImageSchema] = []
    image_url: Optional[str] = None  # 兼容字段：返回逗号分隔的URL字符串
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BlogList(BaseModel):
    total: int
    items: List[Blog]


class BlogCommentBase(BaseModel):
    content: str
    parent_id: Optional[int] = None


class BlogCommentCreate(BlogCommentBase):
    pass


class BlogComment(BlogCommentBase):
    id: int
    blog_id: int
    user_id: int
    username: Optional[str] = None  # 评论者用户名
    parent_username: Optional[str] = None  # 父评论者用户名（如果是回复）
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BlogCommentList(BaseModel):
    total: int
    items: List[BlogComment]
