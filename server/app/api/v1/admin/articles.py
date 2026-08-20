from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.admin.deps import get_current_admin
from app.db.session import get_db
from app.models import AdminUser, Article
from app.schemas.admin import AdminArticleCreate, AdminArticleUpdate
from app.schemas.article import ArticleOut

router = APIRouter(prefix="/admin/articles", tags=["admin-articles"])


def _get(db: Session, article_id: int) -> Article:
    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    return article


@router.get("", response_model=list[ArticleOut])
def admin_list_articles(
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    return list(db.scalars(select(Article).order_by(Article.sort_order.asc(), Article.created_at.desc())).all())


@router.post("", response_model=ArticleOut)
def admin_create_article(
    payload: AdminArticleCreate,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    article = Article(**payload.model_dump())
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@router.put("/{article_id}", response_model=ArticleOut)
def admin_update_article(
    article_id: int,
    payload: AdminArticleUpdate,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    article = _get(db, article_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(article, k, v)
    db.commit()
    db.refresh(article)
    return article


@router.delete("/{article_id}")
def admin_delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    article = _get(db, article_id)
    db.delete(article)
    db.commit()
    return {"detail": "已删除"}