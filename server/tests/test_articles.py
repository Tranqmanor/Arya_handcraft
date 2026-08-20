"""文章模块测试。"""
from app.models import Article


def _add_article(db, **kwargs) -> Article:
    defaults = dict(
        title="测试文章",
        summary="摘要",
        cover_url="",
        content="## 正文",
        category="general",
        view_count=0,
        is_published=True,
        sort_order=0,
    )
    defaults.update(kwargs)
    a = Article(**defaults)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def test_list_articles_only_published(client, db_session):
    db = db_session()
    _add_article(db, title="已发布1", category="photo_guide", sort_order=1)
    _add_article(db, title="草稿", is_published=False)
    db.close()

    resp = client.get("/api/v1/articles")
    assert resp.status_code == 200
    articles = resp.json()
    assert len(articles) == 1
    assert articles[0]["title"] == "已发布1"
    assert articles[0]["category"] == "photo_guide"
    # 列表不含正文
    assert "content" not in articles[0]


def test_article_detail_includes_content(client, db_session):
    db = db_session()
    a = _add_article(db, title="拍照指南")
    article_id = a.id
    db.close()

    resp = client.get(f"/api/v1/articles/{article_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "拍照指南"
    assert resp.json()["content"] == "## 正文"


def test_article_detail_not_found(client):
    resp = client.get("/api/v1/articles/9999")
    assert resp.status_code == 404


def test_article_view_increments(client, db_session):
    db = db_session()
    a = _add_article(db)
    article_id = a.id
    db.close()

    r1 = client.post(f"/api/v1/articles/{article_id}/view")
    assert r1.status_code == 200
    assert r1.json()["view_count"] == 1

    # 文章浏览计数不做去重,每次 +1
    r2 = client.post(f"/api/v1/articles/{article_id}/view")
    assert r2.json()["view_count"] == 2