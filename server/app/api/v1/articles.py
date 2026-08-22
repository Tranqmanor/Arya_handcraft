from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.ratelimit import allow as rate_allow
from app.core.ratelimit import client_ip
from app.db.session import get_db
from app.schemas.article import ArticleListItem, ArticleOut, ArticleViewOut
from app.services.article import get_article, increment_view, list_published_articles

router = APIRouter(prefix="/articles", tags=["articles"])

# 防刷:文章计数无去重,按 IP 放宽限流(超出返回 429)
ARTICLE_VIEW_ATTEMPT_LIMIT = 30
ARTICLE_VIEW_WINDOW_SECONDS = 60.0


@router.get("", response_model=list[ArticleListItem])
def list_articles(db: Session = Depends(get_db)):
    """已发布文章列表(不含正文)。"""
    return list_published_articles(db)


@router.get("/{article_id}", response_model=ArticleOut)
def article_detail(article_id: int, db: Session = Depends(get_db)):
    article = get_article(db, article_id)
    if article is None or not article.is_published:
        raise HTTPException(status_code=404, detail="文章不存在")
    return article


@router.post("/{article_id}/view", response_model=ArticleViewOut)
def add_view(article_id: int, request: Request, db: Session = Depends(get_db)):
    """文章浏览量 +1(按 IP 限流防刷)。"""
    article = get_article(db, article_id)
    if article is None or not article.is_published:
        raise HTTPException(status_code=404, detail="文章不存在")
    if not rate_allow(
        f"article-view:{client_ip(request)}",
        ARTICLE_VIEW_ATTEMPT_LIMIT,
        ARTICLE_VIEW_WINDOW_SECONDS,
    ):
        raise HTTPException(status_code=429, detail="操作过于频繁,请稍后再试")
    count = increment_view(db, article)
    return ArticleViewOut(article_id=article.id, view_count=count, viewed=True)