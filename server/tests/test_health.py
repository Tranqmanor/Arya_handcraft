def test_health(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"
    # 诊断字段:变量注入自检(布尔值/域名列表,不含敏感值)
    diag = data["diagnostics"]
    assert isinstance(diag["database_url_set"], bool)
    assert isinstance(diag["jwt_secret_set"], bool)
    assert isinstance(diag["cors_origins"], list)

