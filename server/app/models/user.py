from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    openid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    unionid: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    nickname: Mapped[str] = mapped_column(String(64), default="")
    avatar_url: Mapped[str] = mapped_column(String, default="")
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
