"""管理端订单管理:总览/定价/收款确认/制作/物流/退款。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.admin.deps import get_current_admin
from app.db.session import get_db
from app.models import AdminUser, Order, User
from app.schemas.order import (
    AdminOrderDetailOut,
    AdminOrderListItem,
    CancelIn,
    ConfirmPaymentIn,
    MakingPhotosIn,
    PriceSetIn,
    RefundIn,
    SetCoverIn,
    ShipIn,
)
from app.services import order_calc as oc
from app.services import orders as order_service
from app.services.orders import OrderError

router = APIRouter(prefix="/admin/orders", tags=["admin-orders"])


def _get_order(db: Session, order_id: int) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


def _base_item(db: Session, order: Order, user: User | None) -> dict:
    return {
        "id": order.id,
        "order_no": order.order_no,
        "status": order.status,
        "status_label": oc.STATUS_LABELS.get(order.status, order.status),
        "cat_name": order.cat_name,
        "user_nickname": (user.nickname if user else "") or "",
        "user_phone": user.phone if user else None,
        "total_price": order.total_price,
        "deposit_due": order.deposit_due,
        "making_due": order.making_due,
        "final_due": order.final_due,
        "paid_deposit": order.paid_deposit,
        "paid_making": order.paid_making,
        "paid_final": order.paid_final,
        "address": order.address_snapshot or {},
        "images": order.images or [],
        "cover_image_url": order.cover_image_url,
        "referrer_user_id": order.referrer_user_id,
        "queue_no": order_service.queue_no(db, order),
        "created_at": order.created_at,
    }


@router.get("", response_model=list[AdminOrderListItem])
def admin_list_orders(
    status: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """订单总览:支持按状态筛选与关键词(单号/猫咪名/客户昵称)搜索。"""
    order_service.sweep_expired_deposit(db)

    stmt = select(Order, User).join(User, Order.user_id == User.id).order_by(Order.created_at.desc())
    if status:
        stmt = stmt.where(Order.status == status)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(Order.order_no.like(like) | Order.cat_name.like(like) | User.nickname.like(like))

    items = []
    for order, user in db.execute(stmt).all():
        item = _base_item(db, order, user)
        items.append(item)
    return items


@router.get("/{order_id}", response_model=AdminOrderDetailOut)
def admin_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    order = _get_order(db, order_id)
    user = db.get(User, order.user_id)
    data = _base_item(db, order, user)
    data.update(
        {
            "requirement": order.requirement,
            "making_photos": order.making_photos or [],
            "shipping_company": order.shipping_company,
            "tracking_no": order.tracking_no,
            "price_note": order.price_note,
            "refund_reason": order.refund_reason,
            "refund_amount": order.refund_amount,
            "cancel_reason": order.cancel_reason,
            "coupon_id": order.coupon_id,
            "coupon_amount": order.coupon_amount,
        }
    )
    return data


@router.put("/{order_id}/price", response_model=AdminOrderDetailOut)
def admin_set_price(
    order_id: int,
    payload: PriceSetIn,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """店长定价:固化三阶段应付(券额自动参与折算)。"""
    order = _get_order(db, order_id)
    try:
        order = order_service.set_price(db, order, payload.total_price, payload.note)
    except OrderError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return admin_order_detail(order_id, db, admin)


@router.put("/{order_id}/confirm-payment", response_model=AdminOrderDetailOut)
def admin_confirm_payment(
    order_id: int,
    payload: ConfirmPaymentIn,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """确认到账(deposit/making/final),写支付流水并推进状态。"""
    order = _get_order(db, order_id)
    try:
        order = order_service.confirm_payment(
            db, order, payload.stage, payload.amount, admin.id, payload.note
        )
    except OrderError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return admin_order_detail(order_id, db, admin)


@router.put("/{order_id}/start-making", response_model=AdminOrderDetailOut)
def admin_start_making(
    order_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """开始制作:排队中 → 待付制作定金(客户侧付款按钮激活)。"""
    order = _get_order(db, order_id)
    try:
        order = order_service.start_making(db, order)
    except OrderError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return admin_order_detail(order_id, db, admin)


@router.put("/{order_id}/finish-making", response_model=AdminOrderDetailOut)
def admin_finish_making(
    order_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """制作完成:制作中 → 待付尾款。"""
    order = _get_order(db, order_id)
    try:
        order = order_service.finish_making(db, order)
    except OrderError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return admin_order_detail(order_id, db, admin)


@router.put("/{order_id}/making-photos", response_model=AdminOrderDetailOut)
def admin_set_making_photos(
    order_id: int,
    payload: MakingPhotosIn,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """上传/更新制作进度照片(≤3 张 URL,经 /admin/uploads/image 获取)。"""
    order = _get_order(db, order_id)
    order.making_photos = list(payload.photos)[:3]
    db.commit()
    db.refresh(order)
    return admin_order_detail(order_id, db, admin)


@router.put("/{order_id}/set-cover", response_model=AdminOrderDetailOut)
def admin_set_cover(
    order_id: int,
    payload: SetCoverIn,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """从客户上传的图片中指定一张作为该订单展示封面(首页作品画廊用)。"""
    order = _get_order(db, order_id)
    if payload.image_url not in (order.images or []):
        raise HTTPException(status_code=400, detail="封面必须是客户上传的图片之一")
    order.cover_image_url = payload.image_url
    db.commit()
    db.refresh(order)
    return admin_order_detail(order_id, db, admin)


@router.put("/{order_id}/ship", response_model=AdminOrderDetailOut)
def admin_ship(
    order_id: int,
    payload: ShipIn,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """写入物流信息并标记已寄出。"""
    order = _get_order(db, order_id)
    try:
        order = order_service.ship_order(db, order, payload.shipping_company, payload.tracking_no)
    except OrderError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return admin_order_detail(order_id, db, admin)


@router.put("/{order_id}/refund", response_model=AdminOrderDetailOut)
def admin_refund(
    order_id: int,
    payload: RefundIn,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """处理退款:记录流水、返还优惠券;定金不退规则由管理员核定退款金额体现。"""
    order = _get_order(db, order_id)
    try:
        order = order_service.admin_refund(db, order, payload.amount, payload.reason, admin.id)
    except OrderError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return admin_order_detail(order_id, db, admin)


@router.put("/{order_id}/cancel", response_model=AdminOrderDetailOut)
def admin_cancel(
    order_id: int,
    payload: CancelIn,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    order = _get_order(db, order_id)
    try:
        order = order_service.admin_cancel(db, order, payload.reason)
    except OrderError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return admin_order_detail(order_id, db, admin)


@router.put("/{order_id}/reopen", response_model=AdminOrderDetailOut)
def admin_reopen(
    order_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """重开已关闭订单(如客户补付定金)。"""
    order = _get_order(db, order_id)
    try:
        order = order_service.admin_reopen(db, order)
    except OrderError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return admin_order_detail(order_id, db, admin)