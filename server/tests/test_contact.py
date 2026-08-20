"""联系店主接口测试。"""


def test_contact_config(client):
    resp = client.get("/api/v1/contact/config")
    assert resp.status_code == 200
    data = resp.json()
    assert "qr_url" in data
    assert data["tip"]