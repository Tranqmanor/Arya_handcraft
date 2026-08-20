from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    video_url: Mapped[str] = mapped_column(Text, nullable=False)  # 竖屏 mp4 地址(Cloudflare R2)
    cover_url: Mapped[str] = mapped_column(Text, default="")
    duration: Mapped[int] = mapped_column(Integer, default=0)  # 时长(秒)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class VideoView(Base):
    """浏览量去重表(防刷)。"""

    __tablename__ = "video_views"
    __table_args__ = (
        Index("idx_video_views_video", "video_id"),
        UniqueConstraint("video_id", "viewer_key", name="uq_video_views"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    video_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("videos.id"), nullable=False)
    viewer_key: Mapped[str] = mapped_column(String(128), nullable=False)  # openid 或会话指纹
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
