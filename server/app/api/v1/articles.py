from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.article import ArticleListItem, ArticleOut, ArticleViewOut
from app.services.article import get_article, increment_view, list_published_articles

router = APIRouter(prefix="/articles", tags=["articles"])


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
def add_view(article_id: int, db: Session = Depends(get_db)):
    """文章浏览量 +1。"""
    article = get_article(db, article_id)
    if article is None or not article.is_published:
        raise HTTPException(status_code=404, detail="文章不存在")
    count = increment_view(db, article)
    return ArticleViewOut(article_id=article.id, view_count=count, viewed=True)