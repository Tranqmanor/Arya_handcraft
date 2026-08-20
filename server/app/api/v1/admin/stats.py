from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.admin.deps import get_current_admin
from app.db.session import get_db
from app.models import AdminUser, Article, Coupon, User, Video

router = APIRouter(prefix="/admin/stats", tags=["admin-stats"])


@router.get("/summary")
def admin_summary(
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """后台概览统计。"""
    user_count = db.scalar(select(func.count(User.id)))
    video_count = db.scalar(select(func.count(Video.id)))
    article_count = db.scalar(select(func.count(Article.id)))
    total_views = (db.scalar(select(func.sum(Video.view_count))) or 0) + (
        db.scalar(select(func.sum(Article.view_count))) or 0
    )
    coupon_count = db.scalar(select(func.count(Coupon.id)))
    unused_coupon_count = db.scalar(
        select(func.count(Coupon.id)).where(Coupon.status == "unused")
    )
    return {
        "user_count": user_count or 0,
        "video_count": video_count or 0,
        "article_count": article_count or 0,
        "total_views": total_views or 0,
        "coupon_count": coupon_count or 0,
        "unused_coupon_count": unused_coupon_count or 0,
    }