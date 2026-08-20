from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.admin.deps import ensure_default_admin, get_current_admin
from app.core.security import create_admin_token, verify_password
from app.db.session import get_db
from app.models import AdminUser
from app.schemas.admin import AdminLoginRequest, AdminTokenResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/auth/login", response_model=AdminTokenResponse)
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    """管理员登录(自动初始化默认 admin 账号)。"""
    ensure_default_admin(db)
    admin = db.scalar(select(AdminUser).where(AdminUser.username == payload.username))
    if admin is None or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return AdminTokenResponse(access_token=create_admin_token(str(admin.id)))