from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Video, VideoView


def list_published_videos(db: Session) -> list[Video]:
    stmt = (
        select(Video)
        .where(Video.is_published.is_(True))
        .order_by(Video.sort_order.asc(), Video.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def get_video(db: Session, video_id: int) -> Video | None:
    return db.get(Video, video_id)


def record_view(db: Session, video: Video, viewer_key: str) -> tuple[int, bool]:
    """记录一次浏览(video_id + viewer_key 去重,重复观看不累加)。"""
    exists = db.scalar(
        select(VideoView).where(
            VideoView.video_id == video.id,
            VideoView.viewer_key == viewer_key,
        )
    )
    if exists:
        return video.view_count, False

    db.add(VideoView(video_id=video.id, viewer_key=viewer_key))
    try:
        video.view_count += 1
        db.commit()
    except IntegrityError:
        # 并发竞态:同一 (video_id, viewer_key) 已被其他请求先插入(唯一约束兜底)
        db.rollback()
        db.refresh(video)
        return video.view_count, False
    return video.view_count, True