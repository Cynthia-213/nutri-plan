from fastapi import APIRouter, Depends, HTTPException, Query, status, Response, UploadFile, File
from sqlalchemy.orm import Session
from typing import Any

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.schemas.blog import (
    BlogCreate,
    BlogUpdate,
    BlogList,
    Blog,
    BlogCommentCreate,
    BlogCommentList,
    BlogComment,
)
from fastapi import Query
from app.services.blog_service import blog_service

router = APIRouter()


@router.get("/", response_model=BlogList)
def list_public_blogs(
    *,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(deps.get_current_active_user_optional),
) -> Any:
    """
    公共社区动态列表（按时间倒序）
    """
    return blog_service.list_public(db, skip=skip, limit=limit, current_user=current_user)


@router.get("/me", response_model=BlogList)
def list_my_blogs(
    *,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    当前用户的动态列表
    """
    return blog_service.list_my(db, user=current_user, skip=skip, limit=limit)


@router.post("/", response_model=Blog, status_code=status.HTTP_201_CREATED)
def create_blog(
    *,
    db: Session = Depends(get_db),
    blog_in: BlogCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    发布一条社区动态
    """
    return blog_service.create(db, user=current_user, obj_in=blog_in)


@router.post("/upload", response_model=dict)
async def upload_image(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    上传图片到 COS（后端中转）
    """
    try:
        file_url = await blog_service.upload_file_to_cos(file=file, user=current_user)
        return {"file_url": file_url}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"上传失败: {str(e)}")


@router.get("/upload-url", response_model=dict)
def generate_upload_url(
    *,
    db: Session = Depends(get_db),
    filename: str = Query(..., description="原始文件名，用于生成后缀"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取 COS 预签名上传 URL
    """
    try:
        return blog_service.generate_upload_url(filename=filename, user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="COS配置缺失或服务不可用")


@router.get("/{blog_id}", response_model=Blog)
def get_blog_detail(
    *,
    db: Session = Depends(get_db),
    blog_id: int,
    current_user: User = Depends(deps.get_current_active_user_optional),
) -> Any:
    """
    获取动态详情
    """
    blog_obj = blog_service.get(db, blog_id=blog_id, current_user=current_user)
    if not blog_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found.")
    return blog_obj


@router.patch("/{blog_id}", response_model=Blog)
def update_blog(
    *,
    db: Session = Depends(get_db),
    blog_id: int,
    blog_in: BlogUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    更新自己的动态
    """
    updated = blog_service.update(db, blog_id=blog_id, user=current_user, obj_in=blog_in)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found or no permission.")
    return updated


@router.post("/{blog_id}/like", response_model=Blog)
def toggle_like_blog(
    *,
    db: Session = Depends(get_db),
    blog_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    切换点赞状态：如果已点赞则取消，否则点赞
    """
    result = blog_service.toggle_like(db, blog_id=blog_id, user=current_user)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found.")
    return result


@router.get("/{blog_id}/comments", response_model=BlogCommentList)
def list_blog_comments(
    *,
    db: Session = Depends(get_db),
    blog_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> Any:
    """
    获取评论列表
    """
    return blog_service.list_comments(db, blog_id=blog_id, skip=skip, limit=limit)


@router.post("/{blog_id}/comments", response_model=BlogComment, status_code=status.HTTP_201_CREATED)
def create_blog_comment(
    *,
    db: Session = Depends(get_db),
    blog_id: int,
    comment_in: BlogCommentCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    发表评论/回复
    """
    # 确认动态存在
    blog_obj = blog_service.get(db, blog_id=blog_id)
    if not blog_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found.")

    return blog_service.create_comment(db, blog_id=blog_id, user=current_user, obj_in=comment_in)


@router.delete(
    "/{blog_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
)
def delete_blog(
    *,
    db: Session = Depends(get_db),
    blog_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    删除自己的动态
    """
    ok = blog_service.delete(db, blog_id=blog_id, user=current_user)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found or no permission.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
