from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_serializer


# ---------- 认证 ----------
class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- 视频管理 ----------
class AdminVideoCreate(BaseModel):
    title: str
    description: str = ""
    video_url: str
    cover_url: str = ""
    duration: int = 0
    is_published: bool = True
    sort_order: int = 0


class AdminVideoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    video_url: str | None = None
    cover_url: str | None = None
    duration: int | None = None
    is_published: bool | None = None
    sort_order: int | None = None


# ---------- 文章管理 ----------
class AdminArticleCreate(BaseModel):
    title: str
    summary: str = ""
    cover_url: str = ""
    content: str
    category: str = "general"
    is_published: bool = True
    sort_order: int = 0


class AdminArticleUpdate(BaseModel):
    title: str | None = None
    summary: str | None = None
    cover_url: str | None = None
    content: str | None = None
    category: str | None = None
    is_published: bool | None = None
    sort_order: int | None = None


# ---------- 优惠券 ----------
class AdminCouponGrant(BaseModel):
    user_id: int
    title: str = "新客立减 20"
    amount: Decimal = Decimal("20")
    expires_days: int | None = 30


class CouponAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    amount: Decimal
    status: str
    created_at: datetime

    @field_serializer("amount")
    def _ser_amount(self, v: Decimal) -> float:
        return float(v)


# ---------- 轮播图管理 ----------
class AdminCarouselImageCreate(BaseModel):
    image_url: str
    title: str = ""
    description: str = ""
    is_published: bool = True
    sort_order: int = 0


class AdminCarouselImageUpdate(BaseModel):
    image_url: str | None = None
    title: str | None = None
    description: str | None = None
    is_published: bool | None = None
    sort_order: int | None = None


# ---------- 用户简表 ----------
class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    openid: str
    nickname: str = ""
    avatar_url: str = ""
    phone: str | None = None
    created_at: datetime