from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Coupon(Base):
    __tablename__ = "coupons"
    __table_args__ = (Index("idx_coupons_user", "user_id", "status"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(64), nullable=False)  # 如「新客立减 20」
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    status: Mapped[str] = mapped_column(String(16), default="unused")  # unused / used / expired
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
