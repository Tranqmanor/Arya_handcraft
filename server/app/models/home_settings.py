from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HomeSettings(Base):
    """首页配置(单行记录,id 恒为 1)。"""

    __tablename__ = "home_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    promo_image_url: Mapped[str] = mapped_column(String, default="")  # 六宫格下方横版宣传图
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
