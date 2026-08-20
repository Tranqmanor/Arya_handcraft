from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.admin.deps import get_current_admin
from app.db.session import get_db
from app.models import AdminUser, Video
from app.schemas.admin import AdminVideoCreate, AdminVideoUpdate
from app.schemas.video import VideoOut

router = APIRouter(prefix="/admin/videos", tags=["admin-videos"])


def _get(db: Session, video_id: int) -> Video:
    video = db.get(Video, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="视频不存在")
    return video


@router.get("", response_model=list[VideoOut])
def admin_list_videos(
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """管理端视频列表(含草稿,按排序)。"""
    from sqlalchemy import select

    return list(db.scalars(select(Video).order_by(Video.sort_order.asc(), Video.created_at.desc())).all())


@router.post("", response_model=VideoOut)
def admin_create_video(
    payload: AdminVideoCreate,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    video = Video(**payload.model_dump())
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


@router.put("/{video_id}", response_model=VideoOut)
def admin_update_video(
    video_id: int,
    payload: AdminVideoUpdate,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    video = _get(db, video_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(video, k, v)
    db.commit()
    db.refresh(video)
    return video


@router.delete("/{video_id}")
def admin_delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    video = _get(db, video_id)
    db.delete(video)
    db.commit()
    return {"detail": "已删除"}