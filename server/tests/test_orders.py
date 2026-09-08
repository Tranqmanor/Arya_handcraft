"""订单模块测试:金额规则/创建/定价/收款推进/排队/超时/退款/推荐奖励。"""
import io

from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.v1.admin.deps import get_current_admin
from app.core.security import create_access_token
from app.main import app as fastapi_app
from app.models import Address, Coupon, Order, User
from app.services.order_calc import settle_amounts


# ---------- helpers ----------

def _add_user(db, openid: str) -> User:
    user = User(openid=openid, nickname="", avatar_url="")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _add_address(db, user_id: int) -> Address:
    address = Address(
        user_id=user_id,
        receiver="张三",
        phone="13800000000",
        region="上海市 上海市 浦东新区",
        detail="某路 1 号",
    )
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


def _add_coupon(db, user_id: int, amount: str = "50") -> Coupon:
    coupon = Coupon(user_id=user_id, title="测试券", amount=amount, status="unused")
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


def _headers(user_id: int) -> dict:
    return {"Authorization": f"Bearer {create_access_token(str(user_id))}"}


class _FakeAdmin:
    id = 1


@contextmanager
def _admin_client(client):
    """临时绕过管理员鉴权(上下文管理器),结束自动清理。"""
    fastapi_app.dependency_overrides[get_current_admin] = lambda: _FakeAdmin()
    yield client
    fastapi_app.dependency_overrides.pop(get_current_admin, None)


def _create_order(client, user_id: int, address_id: int, **extra) -> dict:
    payload = {
        "cat_name": "团子",
        "images": [f"https://r2.example.com/u{i}.jpg" for i in range(3)],
        "address_id": address_id,
        **extra,
    }
    resp = client.post("/api/v1/orders", headers=_headers(user_id), json=payload)
    assert resp.status_code == 200
    return resp.json()


# ---------- 金额规则 ----------

def test_settle_amounts_rules():
    # ≥1000:排队定金 300,制作定金 floor10(30% - 300)
    assert settle_amounts(2122) == (300, 330, 1492)  # 30%=636.6 → 336 → 330
    assert settle_amounts(1000) == (300, 0, 700)
    # <1000:排队定金 floor10(30%),制作定金 0
    assert settle_amounts(800) == (240, 0, 560)
    assert settle_amounts(50) == (10, 0, 40)
    # 券抵扣作用于折后总价
    assert settle_amounts(2172, 50) == (300, 330, 1492)
    assert settle_amounts(950, 500) == (130, 0, 320)  # 折后 450
    assert settle_amounts(300, 500) == (0, 0, 0)  # 券超总价 → 全 0


# ---------- 创建订单 ----------

def test_create_order_requires_auth(client):
    resp = client.post("/api/v1/orders", json={"cat_name": "x", "images": ["a"], "address_id": 1})
    assert resp.status_code == 401


def test_create_order_with_coupon_locks_it(client, db_session):
    db = db_session()
    user = _add_user(db, "openid-order-1")
    address = _add_address(db, user.id)
    coupon = _add_coupon(db, user.id, "50")
    user_id, address_id, coupon_id = user.id, address.id, coupon.id
    db.close()

    body = _create_order(client, user_id, address_id, coupon_id=coupon_id, requirement="蓝白渐变")
    assert body["status"] == "pending_price"
    assert body["queue_no"] == 1

    db = db_session()
    assert db.get(Coupon, coupon_id).status == "used"


def test_create_order_validations(client, db_session):
    db = db_session()
    user = _add_user(db, "openid-order-2")
    other = _add_user(db, "openid-order-3")
    address = _add_address(db, user.id)
    foreign_coupon = _add_coupon(db, other.id)
    user_id, other_id, address_id, foreign_coupon_id = user.id, other.id, address.id, foreign_coupon.id
    db.close()

    # 地址不属于自己
    resp = client.post(
        "/api/v1/orders",
        headers=_headers(user_id),
        json={"cat_name": "x", "images": ["a"], "address_id": address_id + 999},
    )
    assert resp.status_code == 400

    # 图片超过 12 张(pydantic 请求体验证拦截)
    resp = client.post(
        "/api/v1/orders",
        headers=_headers(user_id),
        json={"cat_name": "x", "images": ["a"] * 13, "address_id": address_id},
    )
    assert resp.status_code == 422

    # 券不属于自己
    resp = client.post(
        "/api/v1/orders",
        headers=_headers(user_id),
        json={"cat_name": "x", "images": ["a"], "address_id": address_id, "coupon_id": foreign_coupon_id},
    )
    assert resp.status_code == 400


# ---------- 全生命周期 ----------

def test_full_order_flow(client, db_session):
    db = db_session()
    user = _add_user(db, "openid-flow")
    address = _add_address(db, user.id)
    user_id, address_id = user.id, address.id
    db.close()

    headers = _headers(user_id)
    body = _create_order(client, user_id, address_id)
    order_id = body["id"]

    with _admin_client(client):
        # 定价 → 待付排队定金
        r = client.put(f"/api/v1/admin/orders/{order_id}/price", json={"total_price": 2122, "note": "复杂款"})
        assert r.status_code == 200
        assert (r.json()["deposit_due"], r.json()["making_due"], r.json()["final_due"]) == (300, 330, 1492)
        assert r.json()["status"] == "pending_deposit"

        # 确认排队定金 → 排队中
        r = client.put(
            f"/api/v1/admin/orders/{order_id}/confirm-payment", json={"stage": "deposit", "amount": 300}
        )
        assert r.json()["status"] == "queued"
        assert r.json()["queue_no"] == 1

        # 开始制作 → 待付制作定金(客户按钮激活)
        r = client.put(f"/api/v1/admin/orders/{order_id}/start-making")
        assert r.json()["status"] == "pending_making"

        r = client.put(
            f"/api/v1/admin/orders/{order_id}/confirm-payment", json={"stage": "making", "amount": 330}
        )
        assert r.json()["status"] == "making"

        # 进度照片(≤3)
        r = client.put(
            f"/api/v1/admin/orders/{order_id}/making-photos", json={"photos": ["https://r2/p1.jpg"]}
        )
        assert r.json()["making_photos"] == ["https://r2/p1.jpg"]

        # 制作完成 → 待付尾款 → 确认尾款 → 待寄出
        client.put(f"/api/v1/admin/orders/{order_id}/finish-making")
        r = client.put(
            f"/api/v1/admin/orders/{order_id}/confirm-payment", json={"stage": "final", "amount": 1492}
        )
        assert r.json()["status"] == "ready_to_ship"

        # 寄出
        r = client.put(
            f"/api/v1/admin/orders/{order_id}/ship",
            json={"shipping_company": "顺丰", "tracking_no": "SF0001"},
        )
        assert r.json()["status"] == "shipped"

    # 客户确认收货 → 已完成
    r = client.post(f"/api/v1/orders/{order_id}/confirm-receive", headers=headers)
    assert r.json()["status"] == "completed"
    assert r.json()["queue_no"] == 0


def test_referral_reward_on_final_payment(client, db_session):
    db = db_session()
    referrer = _add_user(db, "openid-ref")
    buyer = _add_user(db, "openid-buyer")
    address = _add_address(db, buyer.id)
    referrer_id, buyer_id, address_id = referrer.id, buyer.id, address.id
    db.close()

    body = _create_order(client, buyer_id, address_id, referrer_user_id=referrer_id)
    order_id = body["id"]

    with _admin_client(client):
        client.put(f"/api/v1/admin/orders/{order_id}/price", json={"total_price": 1500})
        client.put(
            f"/api/v1/admin/orders/{order_id}/confirm-payment", json={"stage": "deposit", "amount": 300}
        )
        client.put(f"/api/v1/admin/orders/{order_id}/start-making")
        client.put(
            f"/api/v1/admin/orders/{order_id}/confirm-payment", json={"stage": "making", "amount": 150}
        )
        client.put(f"/api/v1/admin/orders/{order_id}/finish-making")
        client.put(
            f"/api/v1/admin/orders/{order_id}/confirm-payment", json={"stage": "final", "amount": 1050}
        )

    db = db_session()
    rewards = list(db.scalars(select(Coupon).where(Coupon.user_id == referrer_id)).all())
    assert len(rewards) == 1
    assert float(rewards[0].amount) == 50.0


# ---------- 排队号 / 超时 / 退款 ----------

def test_queue_no_progresses(client, db_session):
    db = db_session()
    u1 = _add_user(db, "openid-q1")
    u2 = _add_user(db, "openid-q2")
    a1 = _add_address(db, u1.id)
    a2 = _add_address(db, u2.id)
    u1_id, u2_id, a1_id, a2_id = u1.id, u2.id, a1.id, a2.id
    db.close()

    first = _create_order(client, u1_id, a1_id)
    second = _create_order(client, u2_id, a2_id)
    assert second["queue_no"] == 2

    with _admin_client(client):
        client.put(f"/api/v1/admin/orders/{first['id']}/price", json={"total_price": 2000})
        client.put(
            f"/api/v1/admin/orders/{first['id']}/confirm-payment", json={"stage": "deposit", "amount": 300}
        )
        # 第一单仍在排队(未交付) → 第二单编号不变
        r = client.get(f"/api/v1/orders/{second['id']}", headers=_headers(u2_id))
        assert r.json()["queue_no"] == 2

        client.put(f"/api/v1/admin/orders/{first['id']}/start-making")
        client.put(
            f"/api/v1/admin/orders/{first['id']}/confirm-payment", json={"stage": "making", "amount": 300}
        )
        client.put(f"/api/v1/admin/orders/{first['id']}/finish-making")
        client.put(
            f"/api/v1/admin/orders/{first['id']}/confirm-payment", json={"stage": "final", "amount": 1400}
        )
        client.put(
            f"/api/v1/admin/orders/{first['id']}/ship",
            json={"shipping_company": "顺丰", "tracking_no": "SF0002"},
        )

    client.post(f"/api/v1/orders/{first['id']}/confirm-receive", headers=_headers(u1_id))

    r = client.get(f"/api/v1/orders/{second['id']}", headers=_headers(u2_id))
    assert r.json()["queue_no"] == 1


def test_deposit_timeout_auto_cancel(client, db_session):
    from datetime import datetime, timedelta, timezone

    db = db_session()
    user = _add_user(db, "openid-timeout")
    address = _add_address(db, user.id)
    user_id, address_id = user.id, address.id
    db.close()

    body = _create_order(client, user_id, address_id)
    order_id = body["id"]

    with _admin_client(client):
        client.put(f"/api/v1/admin/orders/{order_id}/price", json={"total_price": 1200})

    db = db_session()
    order = db.get(Order, order_id)
    order.created_at = datetime.now(timezone.utc) - timedelta(hours=25)
    db.commit()
    db.close()

    # 惰性清理在查询时触发
    client.get("/api/v1/orders", headers=_headers(user_id))
    detail = client.get(f"/api/v1/orders/{order_id}", headers=_headers(user_id))
    assert detail.json()["status"] == "cancelled"

    with _admin_client(client):
        r = client.put(f"/api/v1/admin/orders/{order_id}/reopen")
        assert r.json()["status"] == "pending_deposit"


def test_refund_returns_coupon(client, db_session):
    db = db_session()
    user = _add_user(db, "openid-refund")
    address = _add_address(db, user.id)
    coupon = _add_coupon(db, user.id, "20")
    user_id, address_id, coupon_id = user.id, address.id, coupon.id
    db.close()

    body = _create_order(client, user_id, address_id, coupon_id=coupon_id)
    order_id = body["id"]

    with _admin_client(client):
        client.put(f"/api/v1/admin/orders/{order_id}/price", json={"total_price": 1200})
        client.put(
            f"/api/v1/admin/orders/{order_id}/confirm-payment", json={"stage": "deposit", "amount": 300}
        )

    r = client.post(
        f"/api/v1/orders/{order_id}/refund-request", headers=_headers(user_id), params={"reason": "不想要了"}
    )
    assert r.json()["status"] == "refund_requested"

    with _admin_client(client):
        r = client.put(
            f"/api/v1/admin/orders/{order_id}/refund", json={"amount": 250, "reason": "协商退款"}
        )
        assert r.json()["status"] == "refunded"
        assert r.json()["refund_amount"] == 250

    db = db_session()
    coupon = db.get(Coupon, coupon_id)
    assert coupon.status == "unused"
    assert coupon.used_at is None


# ---------- 作品画廊 ----------

def test_works_lists_completed_with_cover(client, db_session):
    db = db_session()
    user = _add_user(db, "openid-works")
    address = _add_address(db, user.id)
    user_id, address_id = user.id, address.id
    db.close()

    body = _create_order(client, user_id, address_id)
    order_id = body["id"]

    # 未完成且无封面 → 不出现
    resp = client.get("/api/v1/works")
    assert resp.status_code == 200
    assert resp.json() == []

    with _admin_client(client):
        client.put(f"/api/v1/admin/orders/{order_id}/price", json={"total_price": 1000})
        client.put(
            f"/api/v1/admin/orders/{order_id}/confirm-payment", json={"stage": "deposit", "amount": 300}
        )
        client.put(f"/api/v1/admin/orders/{order_id}/start-making")
        client.put(
            f"/api/v1/admin/orders/{order_id}/confirm-payment", json={"stage": "making", "amount": 0}
        )
        client.put(f"/api/v1/admin/orders/{order_id}/finish-making")
        client.put(
            f"/api/v1/admin/orders/{order_id}/confirm-payment", json={"stage": "final", "amount": 700}
        )
        client.put(
            f"/api/v1/admin/orders/{order_id}/ship",
            json={"shipping_company": "顺丰", "tracking_no": "SF0003"},
        )
        client.put(
            f"/api/v1/admin/orders/{order_id}/set-cover", json={"image_url": "https://r2.example.com/u0.jpg"}
        )

    client.post(f"/api/v1/orders/{order_id}/confirm-receive", headers=_headers(user_id))

    resp = client.get("/api/v1/works")
    works = resp.json()
    assert len(works) == 1
    assert works[0]["cat_name"] == "团子"
    assert works[0]["cover_image_url"] == "https://r2.example.com/u0.jpg"


def test_home_settings_public_and_admin(client):
    # 未配置 → 空
    resp = client.get("/api/v1/home-settings")
    assert resp.status_code == 200
    assert resp.json()["promo_image_url"] == ""

    # 管理端更新
    with _admin_client(client):
        r = client.put(
            "/api/v1/admin/home-settings", json={"promo_image_url": "https://r2.example.com/promo.jpg"}
        )
        assert r.status_code == 200

    resp = client.get("/api/v1/home-settings")
    assert resp.json()["promo_image_url"] == "https://r2.example.com/promo.jpg"

    # 未登录不可写
    resp = client.put("/api/v1/admin/home-settings", json={"promo_image_url": "x"})
    assert resp.status_code == 401