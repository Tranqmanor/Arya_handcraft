from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    openid: str
    unionid: str | None = None
    nickname: str = ""
    avatar_url: str = ""
    phone: str | None = None
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    nickname: str | None = None
    avatar_url: str | None = None
    phone: str | None = None