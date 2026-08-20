from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VideoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str = ""
    video_url: str
    cover_url: str = ""
    duration: int = 0
    view_count: int = 0
    sort_order: int = 0
    created_at: datetime


class VideoViewOut(BaseModel):
    video_id: int
    view_count: int
    viewed: bool  # 本次是否算新增浏览量