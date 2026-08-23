"""图片上传接口测试(R2 以桩替换,不发真实网络请求)。"""
import io

import pytest
from fastapi.testclient import TestClient

from app.api.v1.admin.deps import get_current_admin
from app.core.config import get_settings
from app.main import app as fastapi_app
from app.services import storage

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"0" * 64


class _StubS3:
    """替换 boto3 client:记录 put_object / upload_fileobj 调用参数。"""

    def __init__(self):
        self.calls = []
        self.file_calls = []

    def put_object(self, **kwargs):
        self.calls.append(kwargs)
        return {}

    def upload_fileobj(self, fileobj, bucket, key, ExtraArgs=None, Config=None):
        data = fileobj.read()
        self.file_calls.append(
            {"data": data, "Bucket": bucket, "Key": key, "ExtraArgs": ExtraArgs or {}}
        )
        return {}


@pytest.fixture()
def stub_s3(monkeypatch):
    stub = _StubS3()
    # boto3.client 第一个参数为服务名(位置参数),需一并接收
    monkeypatch.setattr(storage.boto3, "client", lambda *_args, **_kw: stub)
    return stub


def _config_r2(monkeypatch, configured: bool = True) -> None:
    """向缓存的 Settings 单例注入/清空 R2 测试配置。"""
    s = get_settings()
    values = {
        "R2_ACCOUNT_ID": "acct",
        "R2_ACCESS_KEY_ID": "key-id",
        "R2_SECRET_ACCESS_KEY": "key-secret",
        "R2_BUCKET_NAME": "bucket",
        "R2_PUBLIC_BASE_URL": "https://pub-test.r2.dev",
    }
    for name, val in values.items():
        monkeypatch.setattr(s, name, val if configured else "")


@pytest.fixture()
def admin_client(client) -> TestClient:
    """绕过管理员鉴权;db_session teardown 会统一清理 overrides。"""
    fastapi_app.dependency_overrides[get_current_admin] = lambda: object()
    yield client
    fastapi_app.dependency_overrides.pop(get_current_admin, None)


def test_upload_requires_auth(client):
    resp = client.post(
        "/api/v1/admin/uploads/image",
        files={"file": ("a.png", io.BytesIO(PNG_BYTES), "image/png")},
    )
    assert resp.status_code == 401


def test_upload_rejects_unsupported_ext(admin_client):
    resp = admin_client.post(
        "/api/v1/admin/uploads/image",
        files={"file": ("note.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert resp.status_code == 400
    assert "jpg/jpeg/png/webp/gif" in resp.json()["detail"]


def test_upload_rejects_content_mismatch(admin_client):
    resp = admin_client.post(
        "/api/v1/admin/uploads/image",
        files={"file": ("fake.png", io.BytesIO(b"plain text, not a png"), "image/png")},
    )
    assert resp.status_code == 400
    assert "扩展名不符" in resp.json()["detail"]


def test_upload_rejects_oversize(admin_client):
    big = b"a" * (storage.MAX_IMAGE_SIZE + 1)
    resp = admin_client.post(
        "/api/v1/admin/uploads/image",
        files={"file": ("big.png", io.BytesIO(big), "image/png")},
    )
    assert resp.status_code == 400
    assert "10MB" in resp.json()["detail"]


def test_upload_fails_when_not_configured(admin_client, monkeypatch):
    _config_r2(monkeypatch, configured=False)
    resp = admin_client.post(
        "/api/v1/admin/uploads/image",
        files={"file": ("a.png", io.BytesIO(PNG_BYTES), "image/png")},
    )
    assert resp.status_code == 503
    assert "未配置" in resp.json()["detail"]


def test_upload_success(admin_client, stub_s3, monkeypatch):
    _config_r2(monkeypatch)
    resp = admin_client.post(
        "/api/v1/admin/uploads/image",
        files={"file": ("cat photo.png", io.BytesIO(PNG_BYTES), "image/png")},
    )
    assert resp.status_code == 200
    url = resp.json()["url"]
    assert url.startswith("https://pub-test.r2.dev/uploads/")
    assert url.endswith(".png")
    # 空格等特殊字符不会出现在存储键中(uuid 命名)
    assert " " not in url

    assert len(stub_s3.calls) == 1
    call = stub_s3.calls[0]
    assert call["Bucket"] == "bucket"
    assert call["ContentType"] == "image/png"
    assert call["Body"] == PNG_BYTES


# ==================== 视频上传 ====================

# ISO-BMFF 头:4 字节 box 长度 + "ftyp" + brand
MP4_BYTES = b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00" + b"0" * 32


def test_validate_video_size_limits():
    storage.validate_video_size(1024)
    with pytest.raises(ValueError):
        storage.validate_video_size(0)
    with pytest.raises(ValueError):
        storage.validate_video_size(storage.MAX_VIDEO_SIZE + 1)


def test_video_rejects_unsupported_ext(admin_client):
    resp = admin_client.post(
        "/api/v1/admin/uploads/video",
        files={"file": ("clip.avi", io.BytesIO(b"x" * 64), "video/x-msvideo")},
    )
    assert resp.status_code == 400
    assert "mp4/mov/m4v/webm" in resp.json()["detail"]


def test_video_rejects_content_mismatch(admin_client):
    resp = admin_client.post(
        "/api/v1/admin/uploads/video",
        files={"file": ("fake.mp4", io.BytesIO(b"plain text, not a video"), "video/mp4")},
    )
    assert resp.status_code == 400
    assert "扩展名不符" in resp.json()["detail"]


def test_video_fails_when_not_configured(admin_client, monkeypatch):
    _config_r2(monkeypatch, configured=False)
    resp = admin_client.post(
        "/api/v1/admin/uploads/video",
        files={"file": ("clip.mp4", io.BytesIO(MP4_BYTES), "video/mp4")},
    )
    assert resp.status_code == 503
    assert "未配置" in resp.json()["detail"]


def test_video_upload_success(admin_client, stub_s3, monkeypatch):
    _config_r2(monkeypatch)
    resp = admin_client.post(
        "/api/v1/admin/uploads/video",
        files={"file": ("my clip.mp4", io.BytesIO(MP4_BYTES), "video/mp4")},
    )
    assert resp.status_code == 200
    url = resp.json()["url"]
    assert url.startswith("https://pub-test.r2.dev/uploads/")
    assert url.endswith(".mp4")
    assert " " not in url

    assert len(stub_s3.file_calls) == 1
    call = stub_s3.file_calls[0]
    assert call["Bucket"] == "bucket"
    assert call["ExtraArgs"]["ContentType"] == "video/mp4"
    # 流式上传:分片读取到的完整内容与原始一致
    assert call["data"] == MP4_BYTES
