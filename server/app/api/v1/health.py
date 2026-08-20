from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter(tags=["system"])


@router.get("/health")
def health(db: Session = Depends(get_db)):
    """健康检查:验证 API 与数据库连通。"""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}
