"""管理端首页配置(横版宣传图等)。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.admin.deps import get_current_admin
from app.db.session import get_db
from app.models import AdminUser, HomeSettings
from app.schemas.order import HomeSettingsIn, HomeSettingsOut

router = APIRouter(prefix="/admin/home-settings", tags=["admin-settings"])


@router.get("", response_model=HomeSettingsOut)
def get_home_settings(
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    settings = db.get(HomeSettings, 1)
    return {"promo_image_url": settings.promo_image_url if settings else ""}


@router.put("", response_model=HomeSettingsOut)
def update_home_settings(
    payload: HomeSettingsIn,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    settings = db.get(HomeSettings, 1)
    if settings is None:
        settings = HomeSettings(id=1)
        db.add(settings)
    settings.promo_image_url = payload.promo_image_url
    db.commit()
    db.refresh(settings)
    return {"promo_image_url": settings.promo_image_url}