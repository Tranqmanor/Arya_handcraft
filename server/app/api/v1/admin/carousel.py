from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.v1.admin.deps import get_current_admin
from app.db.session import get_db
from app.models import AdminUser, CarouselImage
from app.schemas.admin import (
    AdminCarouselImageCreate,
    AdminCarouselImageUpdate,
)
from app.schemas.carousel import CarouselImageOut

router = APIRouter(prefix="/admin/carousel", tags=["admin-carousel"])


def _get(db: Session, carousel_id: int) -> CarouselImage:
    carousel = db.get(CarouselImage, carousel_id)
    if carousel is None:
        raise HTTPException(status_code=404, detail="轮播图不存在")
    return carousel


@router.get("", response_model=list[CarouselImageOut])
def admin_list_carousel(
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """管理端轮播图列表(按排序)。"""
    return list(
        db.scalars(
            select(CarouselImage).order_by(
                CarouselImage.sort_order.asc(), CarouselImage.created_at.asc()
            )
        ).all()
    )


@router.post("", response_model=CarouselImageOut)
def admin_create_carousel(
    payload: AdminCarouselImageCreate,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    carousel = CarouselImage(**payload.model_dump())
    db.add(carousel)
    db.commit()
    db.refresh(carousel)
    return carousel


@router.put("/{carousel_id}", response_model=CarouselImageOut)
def admin_update_carousel(
    carousel_id: int,
    payload: AdminCarouselImageUpdate,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    carousel = _get(db, carousel_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(carousel, k, v)
    db.commit()
    db.refresh(carousel)
    return carousel


@router.delete("/{carousel_id}")
def admin_delete_carousel(
    carousel_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    carousel = _get(db, carousel_id)
    db.delete(carousel)
    db.commit()
    return {"detail": "已删除"}