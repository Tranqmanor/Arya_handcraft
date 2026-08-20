from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.admin.deps import get_current_admin
from app.db.session import get_db
from app.models import AdminUser, Coupon, User
from app.schemas.admin import AdminCouponGrant, CouponAdminOut

router = APIRouter(prefix="/admin/coupons", tags=["admin-coupons"])


@router.post("/grant", response_model=CouponAdminOut)
def admin_grant_coupon(
    payload: AdminCouponGrant,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """给指定用户手动发券。"""
    user = db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    coupon = Coupon(
        user_id=user.id,
        title=payload.title,
        amount=payload.amount,
        status="unused",
        expires_at=(
            datetime.now(timezone.utc) + timedelta(days=payload.expires_days)
            if payload.expires_days
            else None
        ),
    )
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


@router.get("", response_model=list[CouponAdminOut])
def admin_list_coupons(
    user_id: int | None = None,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    stmt = select(Coupon).order_by(Coupon.created_at.desc())
    if user_id is not None:
        stmt = stmt.where(Coupon.user_id == user_id)
    return list(db.scalars(stmt).all())


@router.get("/users", response_model=list[dict])
def admin_search_users(
    q: str = "",
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """根据昵称/openid 前缀查用户,便于发券时选人。"""
    stmt = select(User).order_by(User.created_at.desc()).limit(50)
    if q:
        stmt = stmt.where(User.nickname.like(f"%{q}%") | User.openid.like(f"{q}%"))
    return [
        {"id": u.id, "nickname": u.nickname or f"用户{u.id}", "phone": u.phone}
        for u in db.scalars(stmt).all()
    ]