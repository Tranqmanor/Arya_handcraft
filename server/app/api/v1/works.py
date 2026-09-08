"""公开接口:作品画廊(已完成订单)与首页配置。"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import HomeSettings, Order
from app.schemas.order import HomeSettingsOut, WorkOut

router = APIRouter(tags=["public"])


@router.get("/works", response_model=list[WorkOut])
def list_works(db: Session = Depends(get_db)):
    """成品画廊:已确认收货且设置了展示封面的订单,按完成时间倒序。"""
    rows = list(
        db.scalars(
            select(Order)
            .where(Order.status == "completed", Order.cover_image_url != "")
            .order_by(Order.completed_at.desc())
            .limit(50)
        ).all()
    )
    return [
        {"cat_name": o.cat_name, "cover_image_url": o.cover_image_url, "completed_at": o.completed_at}
        for o in rows
    ]


@router.get("/home-settings", response_model=HomeSettingsOut)
def get_home_settings(db: Session = Depends(get_db)):
    settings = db.get(HomeSettings, 1)
    return {"promo_image_url": settings.promo_image_url if settings else ""}
