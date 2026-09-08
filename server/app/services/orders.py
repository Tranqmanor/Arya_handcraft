"""订单业务:创建/定价/收款推进/取消/退款/排队号/推荐奖励。"""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Address, Coupon, Order, PaymentRecord, User
from app.services import order_calc as oc
from app.services.order_calc import settle_amounts

MAX_ORDER_IMAGES = 12
MAX_ADDRESSES_PER_USER = 6


class OrderError(Exception):
    """业务校验失败,路由层转换为 400。"""


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _gen_order_no() -> str:
    return f"ORD{datetime.now(timezone.utc):%Y%m%d}{uuid.uuid4().hex[:8].upper()}"


def create_order(
    db: Session,
    *,
    user: User,
    cat_name: str,
    images: list[str],
    address_id: int,
    requirement: str = "",
    coupon_id: int | None = None,
    referrer_user_id: int | None = None,
) -> Order:
    """客户提交订单(未定价状态)。核销优惠券并快照地址。"""
    if not (1 <= len(images) <= MAX_ORDER_IMAGES):
        raise OrderError(f"猫咪图片需 1~{MAX_ORDER_IMAGES} 张")

    address = db.get(Address, address_id)
    if address is None or address.user_id != user.id:
        raise OrderError("邮寄地址不存在")

    coupon: Coupon | None = None
    if coupon_id is not None:
        coupon = db.get(Coupon, coupon_id)
        if coupon is None or coupon.user_id != user.id:
            raise OrderError("优惠券不存在")
        if coupon.status != "unused":
            raise OrderError("优惠券已使用或已过期")
        if coupon.expires_at is not None and coupon.expires_at < _now():
            raise OrderError("优惠券已过期")

    if referrer_user_id is not None:
        if referrer_user_id == user.id:
            raise OrderError("推荐人不能是自己")
        if db.get(User, referrer_user_id) is None:
            raise OrderError("推荐人不存在")

    order = Order(
        order_no=_gen_order_no(),
        user_id=user.id,
        referrer_user_id=referrer_user_id,
        cat_name=cat_name.strip()[:64],
        requirement=requirement[:2000],
        images=list(images)[:MAX_ORDER_IMAGES],
        address_snapshot={
            "receiver": address.receiver,
            "phone": address.phone,
            "region": address.region,
            "detail": address.detail,
        },
        coupon_id=coupon.id if coupon else None,
        coupon_amount=int(coupon.amount) if coupon else 0,
        status="pending_price",
    )
    db.add(order)

    # 核销优惠券(条件更新防并发重复使用)
    if coupon is not None:
        updated = (
            db.query(Coupon)
            .filter(Coupon.id == coupon.id, Coupon.status == "unused")
            .update({"status": "used", "used_at": _now()})
        )
        if updated == 0:
            db.rollback()
            raise OrderError("优惠券已使用或已过期")

    db.commit()
    db.refresh(order)
    return order


def set_price(db: Session, order: Order, total_price: int, note: str = "") -> Order:
    """店长定价:固化三阶段应付,状态 → 待付排队定金。"""
    if order.status != "pending_price":
        raise OrderError("当前状态不可定价")
    if total_price <= 0:
        raise OrderError("订单总价必须大于 0")

    deposit_due, making_due, final_due = settle_amounts(total_price, order.coupon_amount)
    order.total_price = total_price
    order.deposit_due = deposit_due
    order.making_due = making_due
    order.final_due = final_due
    order.price_note = note[:255]
    order.status = "pending_deposit"
    db.commit()
    db.refresh(order)
    return order


def confirm_payment(
    db: Session, order: Order, stage: str, amount: int, admin_id: int | None, note: str = ""
) -> Order:
    """管理员确认某阶段到账:写流水并推进状态;尾款确认触发推荐奖励。"""
    transitions = {
        "deposit": ("pending_deposit", "queued", "paid_deposit", "deposit_paid_at"),
        "making": ("pending_making", "making", "paid_making", "making_paid_at"),
        "final": ("pending_final", "ready_to_ship", "paid_final", "final_paid_at"),
    }
    if stage not in transitions:
        raise OrderError("无效的支付阶段")
    if amount < 0:
        raise OrderError("到账金额不能为负")

    required_from, next_status, paid_field, paid_at_field = transitions[stage]
    if order.status != required_from:
        raise OrderError(f"当前状态({order.status})不可确认{stage}款项")

    setattr(order, paid_field, amount)
    setattr(order, paid_at_field, _now())
    order.status = next_status
    db.add(
        PaymentRecord(
            order_id=order.id,
            stage=stage,
            amount=amount,
            channel="manual",
            note=note[:255],
            operator_admin_id=admin_id,
        )
    )
    db.commit()
    db.refresh(order)

    if stage == "final":
        _grant_referral_reward(db, order)
    return order


def _grant_referral_reward(db: Session, order: Order) -> None:
    """被邀请订单尾款到账后,给推荐人发奖励券(幂等:同单只发一次)。"""
    if not order.referrer_user_id:
        return
    exists = db.scalar(
        select(Coupon.id).where(
            Coupon.user_id == order.referrer_user_id,
            Coupon.title == f"{oc.REFERRAL_COUPON_TITLE}#{order.order_no}",
        )
    )
    if exists is not None:
        return
    db.add(
        Coupon(
            user_id=order.referrer_user_id,
            title=f"{oc.REFERRAL_COUPON_TITLE}#{order.order_no}"[:64],
            amount=oc.REFERRAL_COUPON_AMOUNT,
            status="unused",
            expires_at=_now() + timedelta(days=oc.REFERRAL_COUPON_VALID_DAYS),
        )
    )
    db.commit()


def start_making(db: Session, order: Order) -> Order:
    """管理员开始制作:排队中 → 待付制作定金(客户侧按钮由灰变可点)。"""
    if order.status != "queued":
        raise OrderError("仅排队中的订单可开始制作")
    order.status = "pending_making"
    db.commit()
    db.refresh(order)
    return order


def finish_making(db: Session, order: Order) -> Order:
    """管理员制作完成:制作中 → 待付尾款。"""
    if order.status != "making":
        raise OrderError("仅制作中的订单可完成制作")
    order.status = "pending_final"
    db.commit()
    db.refresh(order)
    return order


def ship_order(db: Session, order: Order, shipping_company: str, tracking_no: str) -> Order:
    if order.status != "ready_to_ship":
        raise OrderError("仅待寄出订单可写入物流")
    order.shipping_company = shipping_company[:64]
    order.tracking_no = tracking_no[:64]
    order.status = "shipped"
    order.shipped_at = _now()
    db.commit()
    db.refresh(order)
    return order


def customer_cancel(db: Session, order: Order, reason: str = "") -> Order:
    """客户取消:仅未支付任何款项前允许;排队定金不退(规则文案提示)。"""
    if order.status not in ("pending_price", "pending_deposit"):
        raise OrderError("订单已进入制作流程,如需取消请申请退款")
    order.status = "cancelled"
    order.cancel_reason = reason[:255]
    db.commit()
    db.refresh(order)
    return order


def request_refund(db: Session, order: Order, reason: str) -> Order:
    if order.status not in oc.REFUND_REQUESTABLE:
        raise OrderError("当前状态不可申请退款")
    order.status = "refund_requested"
    order.refund_reason = reason[:255]
    db.commit()
    db.refresh(order)
    return order


def admin_refund(db: Session, order: Order, amount: int, reason: str, admin_id: int | None) -> Order:
    """管理员处理退款:记录流水、返还优惠券(若已核销)。"""
    if order.status in ("completed", "refunded", "cancelled"):
        raise OrderError("当前状态不可退款")

    order.status = "refunded"
    order.refund_amount = amount
    order.refund_reason = (reason or order.refund_reason)[:255]
    db.add(
        PaymentRecord(
            order_id=order.id,
            stage="refund",
            amount=amount,
            channel="manual",
            note=reason[:255],
            operator_admin_id=admin_id,
        )
    )
    if order.coupon_id:
        coupon = db.get(Coupon, order.coupon_id)
        if coupon is not None and coupon.status == "used":
            coupon.status = "unused"
            coupon.used_at = None
    db.commit()
    db.refresh(order)
    return order


def admin_cancel(db: Session, order: Order, reason: str) -> Order:
    if order.status in ("shipped", "completed", "refunded", "cancelled"):
        raise OrderError("当前状态不可关闭")
    order.status = "cancelled"
    order.cancel_reason = reason[:255]
    db.commit()
    db.refresh(order)
    return order


def admin_reopen(db: Session, order: Order) -> Order:
    """关闭订单重开:已定价回到待付排队定金,否则回到待定价。"""
    if order.status != "cancelled":
        raise OrderError("仅已关闭订单可重开")
    order.status = "pending_deposit" if order.total_price else "pending_price"
    db.commit()
    db.refresh(order)
    return order


def sweep_expired_deposit(db: Session) -> int:
    """惰性清理:待付排队定金超过 24h 未确认到账的订单自动关闭。返回关闭数。"""
    deadline = _now() - timedelta(hours=oc.DEPOSIT_TIMEOUT_HOURS)
    expired = list(
        db.scalars(
            select(Order).where(
                Order.status == "pending_deposit",
                Order.created_at < deadline,
            )
        ).all()
    )
    for order in expired:
        order.status = "cancelled"
        order.cancel_reason = "超时未支付排队定金,订单自动关闭"
    if expired:
        db.commit()
    return len(expired)


def queue_no(db: Session, order: Order) -> int:
    """全局排队编号:此前创建且仍占位的订单数 + 1;完结/关闭状态返回 0。"""
    if order.status not in oc.QUEUE_OCCUPYING:
        return 0
    occupied = (
        db.scalar(
            select(func.count(Order.id)).where(
                Order.status.in_(oc.QUEUE_OCCUPYING),
                Order.id != order.id,
                (
                    (Order.created_at < order.created_at)
                    | ((Order.created_at == order.created_at) & (Order.id < order.id))
                ),
            )
        )
        or 0
    )
    return int(occupied) + 1