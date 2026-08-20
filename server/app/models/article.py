from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    summary: Mapped[str] = mapped_column(String(256), default="")
    cover_url: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text, nullable=False)  # 富文本/Markdown 图文
    category: Mapped[str] = mapped_column(String(32), default="general")  # photo_guide=拍照指南
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
