from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Order(Base):
    """羊毛毡猫咪定制订单。"""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    referrer_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )  # 推荐人(分享归因)

    cat_name: Mapped[str] = mapped_column(String(64), default="")
    requirement: Mapped[str] = mapped_column(Text, default="")  # 特殊要求(选填)
    images: Mapped[list] = mapped_column(JSON, default=list)  # 客户上传图片 URL(≤12)
    address_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)  # 下单时地址快照

    total_price: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 店长定价(元,未扣券)
    coupon_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("coupons.id"), nullable=True)
    coupon_amount: Mapped[int] = mapped_column(Integer, default=0)  # 券面额快照(元)

    status: Mapped[str] = mapped_column(String(24), default="pending_price", index=True)

    # 定价时固化的三阶段应付(基于折后总价,元)
    deposit_due: Mapped[int] = mapped_column(Integer, default=0)
    making_due: Mapped[int] = mapped_column(Integer, default=0)
    final_due: Mapped[int] = mapped_column(Integer, default=0)
    # 已确认到账金额(冗余,便于列表与统计)
    paid_deposit: Mapped[int] = mapped_column(Integer, default=0)
    paid_making: Mapped[int] = mapped_column(Integer, default=0)
    paid_final: Mapped[int] = mapped_column(Integer, default=0)

    cover_image_url: Mapped[str] = mapped_column(String, default="")  # 管理员筛图指定的展示封面
    making_photos: Mapped[list] = mapped_column(JSON, default=list)  # 制作进度图(≤3)

    shipping_company: Mapped[str] = mapped_column(String(64), default="")
    tracking_no: Mapped[str] = mapped_column(String(64), default="")

    price_note: Mapped[str] = mapped_column(String(255), default="")
    refund_reason: Mapped[str] = mapped_column(String(255), default="")
    refund_amount: Mapped[int] = mapped_column(Integer, default=0)
    cancel_reason: Mapped[str] = mapped_column(String(255), default="")

    deposit_paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    making_paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    final_paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    shipped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
