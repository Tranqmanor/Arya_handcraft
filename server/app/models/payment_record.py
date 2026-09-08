from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PaymentRecord(Base):
    """订单支付流水(线下确认/未来微信支付统一入口)。

    stage: deposit=排队定金 / making=制作定金 / final=尾款 / refund=退款(负向)
    channel: manual=线下转账后台确认 / wechat_pay=微信支付(预留)
    """

    __tablename__ = "payment_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    stage: Mapped[str] = mapped_column(String(16), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # 元(退款为正数,统计时作负向)
    channel: Mapped[str] = mapped_column(String(16), default="manual")
    note: Mapped[str] = mapped_column(String(255), default="")
    operator_admin_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
