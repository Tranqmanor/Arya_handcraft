"""用户端订单接口(小程序 token 鉴权)。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.users import get_current_user_dep
from app.db.session import get_db
from app.models import Order, User
from app.schemas.order import OrderCreateIn, OrderDetailOut, OrderListItem
from app.services import order_calc as oc
from app.services import orders as order_service
from app.services.orders import OrderError

router = APIRouter(prefix="/orders", tags=["orders"])


def _get_own_order(db: Session, user: User, order_id: int) -> Order:
    order = db.get(Order, order_id)
    if order is None or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


def _list_item(db: Session, order: Order) -> dict:
    return {
        "id": order.id,
        "order_no": order.order_no,
        "cat_name": order.cat_name,
        "status": order.status,
        "status_label": oc.STATUS_LABELS.get(order.status, order.status),
        "total_price": order.total_price,
        "deposit_due": order.deposit_due,
        "making_due": order.making_due,
        "final_due": order.final_due,
        "paid_deposit": order.paid_deposit,
        "paid_making": order.paid_making,
        "paid_final": order.paid_final,
        "cover_image_url": order.cover_image_url,
        "queue_no": order_service.queue_no(db, order),
        "created_at": order.created_at,
    }


@router.get("", response_model=list[OrderListItem])
def list_my_orders(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_dep),
):
    """我的订单(含惰性清理超时未付定金的订单)。"""
    order_service.sweep_expired_deposit(db)
    rows = list(
        db.scalars(select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc())).all()
    )
    return [_list_item(db, o) for o in rows]


@router.post("", response_model=OrderListItem)
def create_order(
    payload: OrderCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_dep),
):
    """提交订单:进入待定价状态,排队定金金额待店长定价后可见。"""
    try:
        order = order_service.create_order(
            db,
            user=user,
            cat_name=payload.cat_name,
            images=payload.images,
            address_id=payload.address_id,
            requirement=payload.requirement,
            coupon_id=payload.coupon_id,
            referrer_user_id=payload.referrer_user_id,
        )
    except OrderError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _list_item(db, order)


@router.get("/{order_id}", response_model=OrderDetailOut)
def order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_dep),
):
    order_service.sweep_expired_deposit(db)
    order = _get_own_order(db, user, order_id)
    data = _list_item(db, order)
    data.update(
        {
            "images": order.images or [],
            "requirement": order.requirement,
            "address": order.address_snapshot or {},
            "making_photos": order.making_photos or [],
            "shipping_company": order.shipping_company,
            "tracking_no": order.tracking_no,
            "price_note": order.price_note,
            "refund_reason": order.refund_reason,
            "refund_amount": order.refund_amount,
            "cancel_reason": order.cancel_reason,
            "coupon_amount": order.coupon_amount,
        }
    )
    return data


@router.post("/{order_id}/cancel", response_model=OrderListItem)
def cancel_order(
    order_id: int,
    reason: str = "",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_dep),
):
    """未付款阶段取消(排队定金不退,规则已在下单页提示)。"""
    order = _get_own_order(db, user, order_id)
    try:
        order = order_service.customer_cancel(db, order, reason)
    except OrderError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _list_item(db, order)


@router.post("/{order_id}/refund-request", response_model=OrderListItem)
def request_refund(
    order_id: int,
    reason: str = "",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_dep),
):
    """申请退款(已付排队定金后)。由管理员核定金额处理。"""
    order = _get_own_order(db, user, order_id)
    try:
        order = order_service.request_refund(db, order, reason)
    except OrderError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _list_item(db, order)


@router.post("/{order_id}/confirm-receive", response_model=OrderListItem)
def confirm_receive(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_dep),
):
    order = _get_own_order(db, user, order_id)
    if order.status != "shipped":
        raise HTTPException(status_code=400, detail="仅已寄出订单可确认收货")
    from app.services.orders import _now

    order.status = "completed"
    order.completed_at = _now()
    db.commit()
    db.refresh(order)
    return _list_item(db, order)