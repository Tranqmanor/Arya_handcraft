from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models import CarouselImage
from app.schemas.carousel import CarouselImageOut

router = APIRouter(prefix="/carousel", tags=["carousel"])


@router.get("", response_model=list[CarouselImageOut])
def list_carousel_images(db: Session = Depends(get_db)):
    """已发布轮播图列表(按排序)。"""
    return list(
        db.scalars(
            select(CarouselImage)
            .where(CarouselImage.is_published == True)
            .order_by(CarouselImage.sort_order.asc(), CarouselImage.created_at.asc())
        ).all()
    )