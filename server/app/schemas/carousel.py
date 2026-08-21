from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CarouselImageOut(BaseModel):
    """公开轮播图输出。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_url: str
    title: str = ""
    description: str = ""
    sort_order: int = 0
    created_at: datetime