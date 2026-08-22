"""视频模块测试。"""
from app.core.security import create_access_token
from app.models import User, Video


def _add_video(db, **kwargs) -> Video:
    defaults = dict(
        title="测试猫咪",
        description="竖屏示例",
        video_url="https://r2.example.com/v1.mp4",
        cover_url="",
        duration=45,
        view_count=0,
        is_published=True,
        sort_order=0,
    )
    defaults.update(kwargs)
    v = Video(**defaults)
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def test_list_videos_only_published(client, db_session):
    db = db_session()
    _add_video(db, title="已发布1", sort_order=1)
    _add_video(db, title="已发布2", sort_order=0)
    _add_video(db, title="草稿", is_published=False)
    db.close()

    resp = client.get("/api/v1/videos")
    assert resp.status_code == 200
    videos = resp.json()
    assert len(videos) == 2
    # sort_order 升序
    assert videos[0]["title"] == "已发布2"


def test_video_detail_not_found(client):
    resp = client.get("/api/v1/videos/9999")
    assert resp.status_code == 404


def test_view_increments_once_per_user(client, db_session):
    db = db_session()
    v = _add_video(db)
    user = User(openid="openid-video-1", nickname="", avatar_url="", phone=None)
    db.add(user)
    db.commit()
    db.refresh(user)
    user_id = user.id
    video_id = v.id
    db.close()

    headers = {"Authorization": f"Bearer {create_access_token(str(user_id))}"}

    r1 = client.post(f"/api/v1/videos/{video_id}/view", headers=headers)
    assert r1.status_code == 200
    assert r1.json()["viewed"] is True
    assert r1.json()["view_count"] == 1

    # 同一用户重复观看不累加
    r2 = client.post(f"/api/v1/videos/{video_id}/view", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["viewed"] is False
    assert r2.json()["view_count"] == 1


def test_view_anonymous_uses_viewer_key(client, db_session):
    db = db_session()
    v = _add_video(db)
    video_id = v.id
    db.close()

    r1 = client.post(f"/api/v1/videos/{video_id}/view", params={"viewer_key": "device-abc"})
    assert r1.json()["view_count"] == 1

    # 不同设备指纹算新增
    r2 = client.post(f"/api/v1/videos/{video_id}/view", params={"viewer_key": "device-def"})
    assert r2.json()["view_count"] == 2

    # 相同设备指纹不累加
    r3 = client.post(f"/api/v1/videos/{video_id}/view", params={"viewer_key": "device-abc"})
    assert r3.json()["view_count"] == 2
    assert r3.json()["viewed"] is False


def test_view_rate_limited_per_ip(client, db_session, monkeypatch):
    """同一 IP 超过上报阈值后应返回 429(防换 key 刷量)。"""
    from app.api.v1 import videos as videos_api

    db = db_session()
    v = _add_video(db)
    video_id = v.id
    db.close()

    monkeypatch.setattr(videos_api, "VIEW_ATTEMPT_LIMIT", 3)

    for _ in range(3):
        resp = client.post(f"/api/v1/videos/{video_id}/view")
        assert resp.status_code == 200

    blocked = client.post(f"/api/v1/videos/{video_id}/view")
    assert blocked.status_code == 429


def test_view_same_key_different_ip_counts_again(client, db_session):
    """同一指纹来自不同来源 IP → 服务端组合键不同,计为新观众。"""
    db = db_session()
    v = _add_video(db)
    video_id = v.id
    db.close()

    url = f"/api/v1/videos/{video_id}/view"
    r1 = client.post(url, params={"viewer_key": "device-x"})
    assert r1.json()["view_count"] == 1

    r2 = client.post(
        url,
        params={"viewer_key": "device-x"},
        headers={"X-Forwarded-For": "203.0.113.9"},
    )
    assert r2.status_code == 200
    assert r2.json()["view_count"] == 2