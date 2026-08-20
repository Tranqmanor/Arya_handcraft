from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Article


def list_published_articles(db: Session) -> list[Article]:
    stmt = (
        select(Article)
        .where(Article.is_published.is_(True))
        .order_by(Article.sort_order.asc(), Article.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def get_article(db: Session, article_id: int) -> Article | None:
    return db.get(Article, article_id)


def increment_view(db: Session, article: Article) -> int:
    """文章浏览 +1(不做去重,纯计数)。"""
    article.view_count += 1
    db.commit()
    return article.view_count