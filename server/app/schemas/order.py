from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------- 用户端:创建订单 ----------
class OrderCreateIn(BaseModel):
    cat_name: str = Field(min_length=1, max_length=64)
    images: list[str] = Field(min_length=1, max_length=12)
    address_id: int
    requirement: str = Field(default="", max_length=2000)
    coupon_id: int | None = None
    referrer_user_id: int | None = None


class OrderListItem(BaseModel):
    id: int
    order_no: str
    cat_name: str
    status: str
    status_label: str = ""
    total_price: int | None = None
    deposit_due: int = 0
    making_due: int = 0
    final_due: int = 0
    paid_deposit: int = 0
    paid_making: int = 0
    paid_final: int = 0
    cover_image_url: str = ""
    queue_no: int = 0
    created_at: datetime


class OrderDetailOut(OrderListItem):
    images: list[str] = []
    requirement: str = ""
    address: dict = {}
    making_photos: list[str] = []
    shipping_company: str = ""
    tracking_no: str = ""
    price_note: str = ""
    refund_reason: str = ""
    refund_amount: int = 0
    cancel_reason: str = ""
    coupon_amount: int = 0


# ---------- 地址簿 ----------
class AddressIn(BaseModel):
    receiver: str = Field(min_length=1, max_length=64)
    phone: str = Field(min_length=5, max_length=20)
    region: str = Field(default="", max_length=128)
    detail: str = Field(default="", max_length=500)
    is_default: bool = False


class AddressOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    receiver: str
    phone: str
    region: str
    detail: str
    is_default: bool
    created_at: datetime


# ---------- 公开:作品画廊 / 首页配置 ----------
class WorkOut(BaseModel):
    cat_name: str
    cover_image_url: str
    completed_at: datetime | None = None


class HomeSettingsOut(BaseModel):
    promo_image_url: str = ""


class HomeSettingsIn(BaseModel):
    promo_image_url: str = Field(default="", max_length=500)


# ---------- 管理端 ----------
class PriceSetIn(BaseModel):
    total_price: int = Field(gt=0)
    note: str = Field(default="", max_length=255)


class ConfirmPaymentIn(BaseModel):
    stage: str = Field(pattern="^(deposit|making|final)$")
    # 允许 0:低总价订单的制作定金可为 0(免付阶段,确认即推进状态)
    amount: int = Field(ge=0)
    note: str = Field(default="", max_length=255)


class MakingPhotosIn(BaseModel):
    photos: list[str] = Field(max_length=3)


class SetCoverIn(BaseModel):
    image_url: str = Field(min_length=1)


class ShipIn(BaseModel):
    shipping_company: str = Field(min_length=1, max_length=64)
    tracking_no: str = Field(min_length=1, max_length=64)


class RefundIn(BaseModel):
    amount: int = Field(gt=0)
    reason: str = Field(default="", max_length=255)


class CancelIn(BaseModel):
    reason: str = Field(default="", max_length=255)


class AdminOrderListItem(BaseModel):
    id: int
    order_no: str
    status: str
    status_label: str = ""
    cat_name: str
    user_nickname: str = ""
    user_phone: str | None = None
    total_price: int | None = None
    deposit_due: int = 0
    making_due: int = 0
    final_due: int = 0
    paid_deposit: int = 0
    paid_making: int = 0
    paid_final: int = 0
    address: dict = {}
    images: list[str] = []
    cover_image_url: str = ""
    referrer_user_id: int | None = None
    queue_no: int = 0
    created_at: datetime


class AdminOrderDetailOut(AdminOrderListItem):
    requirement: str = ""
    making_photos: list[str] = []
    shipping_company: str = ""
    tracking_no: str = ""
    price_note: str = ""
    refund_reason: str = ""
    refund_amount: int = 0
    cancel_reason: str = ""
    coupon_id: int | None = None
    coupon_amount: int = 0