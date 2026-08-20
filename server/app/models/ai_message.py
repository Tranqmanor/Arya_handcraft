from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AiMessage(Base):
    """Arya 对话记录(长期记忆)。"""

    __tablename__ = "ai_messages"
    __table_args__ = (Index("idx_ai_messages_user", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)  # user / assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[str | None] = mapped_column(String(32), nullable=True)  # call_master / info / smalltalk
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
