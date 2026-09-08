from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.admin.deps import get_current_admin
from app.db.session import get_db
from app.models import AdminUser, Article, Coupon, Order, PaymentRecord, User, Video

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


@router.get("/finance")
def admin_finance(
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """账目统计:状态分布/已收/待收/退款/月度流水。"""
    status_rows = db.execute(select(Order.status, func.count(Order.id))).all()
    by_status = {status: count for status, count in status_rows}

    orders = list(db.scalars(select(Order)).all())
    received_deposit = sum(o.paid_deposit or 0 for o in orders)
    received_making = sum(o.paid_making or 0 for o in orders)
    received_final = sum(o.paid_final or 0 for o in orders)
    received_total = received_deposit + received_making + received_final
    refunded_total = sum(o.refund_amount or 0 for o in orders if o.status == "refunded")

    # 待收金额(活跃订单中尚未确认到账的应付部分)
    pending = 0
    for o in orders:
        if o.status == "pending_deposit":
            pending += max(0, (o.deposit_due or 0) - (o.paid_deposit or 0))
        elif o.status == "pending_making":
            pending += max(0, (o.making_due or 0) - (o.paid_making or 0))
        elif o.status == "pending_final":
            pending += max(0, (o.final_due or 0) - (o.paid_final or 0))

    # 月度流水(Python 侧聚合,兼容 SQLite/PG)
    records = list(db.scalars(select(PaymentRecord)).all())
    monthly: dict[str, dict] = {}
    for record in records:
        month = record.created_at.strftime("%Y-%m")
        bucket = monthly.setdefault(month, {"income": 0, "refund": 0})
        if record.stage == "refund":
            bucket["refund"] += record.amount
        else:
            bucket["income"] += record.amount
    monthly_list = [
        {"month": m, "income": v["income"], "refund": v["refund"], "net": v["income"] - v["refund"]}
        for m, v in sorted(monthly.items())
    ]

    return {
        "order_count_by_status": by_status,
        "received": {
            "deposit": received_deposit,
            "making": received_making,
            "final": received_final,
            "total": received_total,
        },
        "refunded_total": refunded_total,
        "net_total": received_total - refunded_total,
        "pending_amount": pending,
        "monthly": monthly_list,
    }