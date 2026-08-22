import hashlib

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.v1.users import get_current_user
from app.core.ratelimit import allow as rate_allow
from app.core.ratelimit import client_ip
from app.db.session import get_db
from app.models import User, Video
from app.schemas.video import VideoOut, VideoViewOut
from app.services.video import get_video, list_published_videos, record_view

router = APIRouter(prefix="/videos", tags=["videos"])

# 防刷:每 IP 每 window 秒内最多上报次数(超出返回 429)
VIEW_ATTEMPT_LIMIT = 10
VIEW_WINDOW_SECONDS = 60.0


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
    request: Request,
    db: Session = Depends(get_db),
    viewer_key: str = "anonymous",
    authorization: str = Header(default=""),
):
    """上报浏览量(去重 + IP 限流)。

    - 已登录用户:用 user.id 作去重键(优先)
    - 未登录用户:服务端将设备指纹与来源 IP 组合哈希后作为去重键
      (客户端传入的裸 key 不可信任),并按 IP 限流防止换 key 刷量
    """
    video = db.get(Video, video_id)
    if video is None or not video.is_published:
        raise HTTPException(status_code=404, detail="视频不存在")

    ip = client_ip(request)
    if not rate_allow(f"video-view:{ip}", VIEW_ATTEMPT_LIMIT, VIEW_WINDOW_SECONDS):
        raise HTTPException(status_code=429, detail="操作过于频繁,请稍后再试")

    key = viewer_key
    if authorization.startswith("Bearer "):
        try:
            user: User = get_current_user(authorization, db)
            key = f"user:{user.id}"
        except HTTPException:
            pass

    # 未登录:指纹与 IP 组合哈希,提高伪造/跨端刷量成本
    if not key.startswith("user:"):
        digest = hashlib.sha256(f"{key}:{ip}".encode("utf-8")).hexdigest()[:32]
        key = f"dev:{digest}"

    view_count, viewed = record_view(db, video, key)
    return VideoViewOut(video_id=video.id, view_count=view_count, viewed=viewed)