from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ArticleListItem(BaseModel):
    """文章列表项(不含正文)。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: str = ""
    cover_url: str = ""
    category: str = "general"
    view_count: int = 0
    sort_order: int = 0
    created_at: datetime


class ArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: str = ""
    cover_url: str = ""
    content: str
    category: str = "general"
    view_count: int = 0
    sort_order: int = 0
    created_at: datetime
    updated_at: datetime


class ArticleViewOut(BaseModel):
    article_id: int
    view_count: int
    viewed: bool