"""认证与用户模块测试。"""
from unittest.mock import patch

from app.core.security import create_access_token
from app.models import Coupon, User
from app.schemas.auth import TokenResponse

FAKE_OPENID = "fake-openid-001"
FAKE_UNIONID = "fake-unionid-001"


def fake_code2session(code: str) -> dict:
    return {"openid": FAKE_OPENID, "unionid": FAKE_UNIONID, "session_key": "fake_session_key"}


def test_login_new_user_gets_token_and_coupon(client, db_session):
    with patch("app.api.v1.auth.code2session", side_effect=fake_code2session):
        resp = client.post("/api/v1/auth/login", json={"code": "wx-code"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["access_token"]
    assert data["refresh_token"]

    # 新用户应自动获得一张新客券
    db = db_session()
    user = db.query(User).filter(User.openid == FAKE_OPENID).one()
    coupon = db.query(Coupon).filter(Coupon.user_id == user.id).one()
    assert coupon.title == "新客立减 20"
    assert coupon.status == "unused"
    db.close()


def test_login_existing_user_no_duplicate_coupon(client, db_session):
    # 先登录一次创建用户
    with patch("app.api.v1.auth.code2session", side_effect=fake_code2session):
        client.post("/api/v1/auth/login", json={"code": "wx-code"})

    # 再次登录不应重复发券
    with patch("app.api.v1.auth.code2session", side_effect=fake_code2session):
        resp = client.post("/api/v1/auth/login", json={"code": "wx-code"})
    assert resp.status_code == 200

    db = db_session()
    user = db.query(User).filter(User.openid == FAKE_OPENID).one()
    coupons = db.query(Coupon).filter(Coupon.user_id == user.id).all()
    assert len(coupons) == 1
    db.close()


def test_get_me_requires_auth(client, db_session):
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 401


def test_get_me_and_update_profile(client, db_session):
    db = db_session()
    user = User(openid=FAKE_OPENID, unionid=FAKE_UNIONID, nickname="旧名", avatar_url="", phone=None)
    db.add(user)
    db.commit()
    db.refresh(user)
    user_id = user.id
    db.close()

    headers = {"Authorization": f"Bearer {create_access_token(str(user_id))}"}

    me = client.get("/api/v1/users/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["openid"] == FAKE_OPENID

    updated = client.put(
        "/api/v1/users/me",
        headers=headers,
        json={"nickname": "阿茶", "phone": "13800138000", "avatar_url": "https://x/avatar.png"},
    )
    assert updated.status_code == 200
    assert updated.json()["nickname"] == "阿茶"
    assert updated.json()["phone"] == "13800138000"


def test_me_coupons(client, db_session):
    db = db_session()
    user = User(openid=FAKE_OPENID, unionid=FAKE_UNIONID, nickname="", avatar_url="", phone=None)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.add(Coupon(user_id=user.id, title="新客立减 20", amount="20", status="unused"))
    db.commit()
    user_id = user.id
    db.close()

    resp = client.get(
        "/api/v1/users/me/coupons",
        headers={"Authorization": f"Bearer {create_access_token(str(user_id))}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "新客立减 20"
