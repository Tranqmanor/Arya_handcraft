from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Coupon

# 新客券配置(后续 M8 后台可配置化)
NEW_USER_COUPON_TITLE = "新客立减 20"
NEW_USER_COUPON_AMOUNT = "20"
NEW_USER_COUPON_VALID_DAYS = 30


def grant_new_user_coupon(db: Session, user_id: int) -> Coupon:
    """新用户注册成功后自动发放一张优惠券。"""
    coupon = Coupon(
        user_id=user_id,
        title=NEW_USER_COUPON_TITLE,
        amount=NEW_USER_COUPON_AMOUNT,
        status="unused",
        expires_at=datetime.now(timezone.utc) + timedelta(days=NEW_USER_COUPON_VALID_DAYS),
    )
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


def list_user_coupons(db: Session, user_id: int) -> list[Coupon]:
    stmt = (
        select(Coupon)
        .where(Coupon.user_id == user_id)
        .order_by(Coupon.created_at.desc())
    )
    return list(db.scalars(stmt).all())