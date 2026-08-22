from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db

router = APIRouter(tags=["system"])


@router.get("/health")
def health(db: Session = Depends(get_db)):
    """健康检查:验证 API 与数据库连通;附带关键环境变量注入自检(不含敏感值)。"""
    db.execute(text("SELECT 1"))
    settings = get_settings()
    return {
        "status": "ok",
        "database": "ok",
        "env": settings.ENV,
        "diagnostics": {
            "database_url_set": bool(settings.DATABASE_URL),
            "jwt_secret_set": bool(settings.JWT_SECRET),
            "wx_app_id_set": bool(settings.WX_APP_ID),
            "wx_app_secret_set": bool(settings.WX_APP_SECRET),
            "llm_api_key_set": bool(settings.LLM_API_KEY),
            "llm_model": settings.LLM_MODEL,
            "admin_password_set": bool(settings.ADMIN_INIT_PASSWORD),
            "cors_origins": settings.cors_origin_list,
        },
    }
