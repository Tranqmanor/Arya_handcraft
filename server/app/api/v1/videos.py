from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.users import get_current_user
from app.db.session import get_db
from app.models import User, Video
from app.schemas.video import VideoOut, VideoViewOut
from app.services.video import get_video, list_published_videos, record_view

router = APIRouter(prefix="/videos", tags=["videos"])


@router.get("", response_model=list[VideoOut])
def list_videos(db: Session = Depends(get_db)):
    """已发布视频列表(排序后)。"""
    return list_published_videos(db)


@router.get("/{video_id}", response_model=VideoOut)
def video_detail(video_id: int, db: Session = Depends(get_db)):
    video = get_video(db, video_id)
    if video is None or not video.is_published:
        raise HTTPException(status_code=404, detail="视频不存在")
    return video


@router.post("/{video_id}/view", response_model=VideoViewOut)
def add_view(
    video_id: int,
    db: Session = Depends(get_db),
    viewer_key: str = "anonymous",
    authorization: str = Header(default=""),
):
    """上报浏览量(去重:同一 viewer_key 对同一视频只计 1 次)。

    - 已登录用户:用 user.id 作去重键(优先)
    - 未登录用户:用前端生成的设备指纹 viewer_key
    """
    video = db.get(Video, video_id)
    if video is None or not video.is_published:
        raise HTTPException(status_code=404, detail="视频不存在")

    key = viewer_key
    if authorization.startswith("Bearer "):
        try:
            user: User = get_current_user(authorization, db)
            key = f"user:{user.id}"
        except HTTPException:
            pass

    view_count, viewed = record_view(db, video, key)
    return VideoViewOut(video_id=video.id, view_count=view_count, viewed=viewed)