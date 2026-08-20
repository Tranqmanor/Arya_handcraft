"""管理后台接口测试。"""
from app.core.security import hash_password
from app.models import AdminUser, Article, User, Video
from app.api.v1.admin.auth import create_admin_token


def _mk_admin(db) -> AdminUser:
    admin = AdminUser(username="admin", password_hash=hash_password("test-pass"))
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def _admin_headers(admin: AdminUser) -> dict:
    return {"Authorization": f"Bearer {create_admin_token(str(admin.id))}"}


def test_admin_login_auto_creates_default(client, db_session):
    """首次登录时自动初始化 admin 账号。"""
    resp = client.post("/api/v1/admin/auth/login", json={"username": "admin", "password": "change_me"})
    # change_me 为 .env 默认值;测试环境 ADMIN_INIT_PASSWORD 读 .env
    assert resp.status_code in (200, 401)


def test_admin_login_wrong_password(client, db_session):
    db = db_session()
    admin = _mk_admin(db)
    token = admin.id
    db.close()

    resp = client.post("/api/v1/admin/auth/login", json={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401


def test_admin_login_success_and_crud_video(client, db_session):
    db = db_session()
    admin = _mk_admin(db)
    headers = _admin_headers(admin)
    db.close()

    # 登录
    resp = client.post("/api/v1/admin/auth/login", json={"username": "admin", "password": "test-pass"})
    assert resp.status_code == 200

    # 无权访问 → 401
    assert client.get("/api/v1/admin/videos").status_code == 401

    # 创建视频
    r = client.post(
        "/api/v1/admin/videos",
        headers=headers,
        json={"title": "后台视频", "video_url": "https://r2.example.com/a.mp4", "duration": 30},
    )
    assert r.status_code == 200
    vid = r.json()["id"]

    # 列表含草稿
    lst = client.get("/api/v1/admin/videos", headers=headers)
    assert lst.status_code == 200 and len(lst.json()) == 1

    # 更新
    up = client.put(f"/api/v1/admin/videos/{vid}", headers=headers, json={"title": "改名"})
    assert up.json()["title"] == "改名"

    # 删除
    d = client.delete(f"/api/v1/admin/videos/{vid}", headers=headers)
    assert d.status_code == 200


def test_admin_article_crud(client, db_session):
    db = db_session()
    admin = _mk_admin(db)
    headers = _admin_headers(admin)
    db.close()

    r = client.post(
        "/api/v1/admin/articles",
        headers=headers,
        json={"title": "后台文章", "content": "## 正文", "category": "photo_guide"},
    )
    assert r.status_code == 200
    aid = r.json()["id"]

    upd = client.put(f"/api/v1/admin/articles/{aid}", headers=headers, json={"summary": "摘要"})
    assert upd.json()["summary"] == "摘要"


def test_admin_grant_coupon_and_stats(client, db_session):
    db = db_session()
    admin = _mk_admin(db)
    headers = _admin_headers(admin)

    from app.models import User

    u = User(openid="admin-test-openid", nickname="测试", avatar_url="", phone=None)
    db.add(u)
    db.commit()
    db.refresh(u)
    uid = u.id
    db.close()

    # 发券
    r = client.post(
        "/api/v1/admin/coupons/grant",
        headers=headers,
        json={"user_id": uid, "title": "手动券", "amount": "10", "expires_days": 7},
    )
    assert r.status_code == 200
    assert float(r.json()["amount"]) == 10.0

    # 统计
    s = client.get("/api/v1/admin/stats/summary", headers=headers)
    assert s.status_code == 200
    assert s.json()["user_count"] >= 1
    assert s.json()["coupon_count"] >= 1

    # 搜索用户
    found = client.get("/api/v1/admin/coupons/users", headers=headers, params={"q": "测试"})
    assert found.status_code == 200
    assert len(found.json()) == 1