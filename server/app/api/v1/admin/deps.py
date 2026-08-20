from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models import AdminUser


def ensure_default_admin(db: Session) -> None:
    """首次运行时创建默认管理员 admin(密码来自 .env ADMIN_INIT_PASSWORD)。"""
    from app.core.config import get_settings
    from app.core.security import hash_password

    exists = db.scalar(select(AdminUser).where(AdminUser.username == "admin"))
    if exists is not None:
        return
    password = get_settings().ADMIN_INIT_PASSWORD
    admin = AdminUser(username="admin", password_hash=hash_password(password))
    db.add(admin)
    db.commit()


def get_current_admin(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> AdminUser:
    """FastAPI 依赖:校验管理员 token 并返回 AdminUser。"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization.removeprefix("Bearer ").strip()
    sub = decode_token(token, expected_type="admin")
    if sub is None:
        raise HTTPException(status_code=401, detail="管理员 token 无效或已过期")
    admin = db.get(AdminUser, int(sub))
    if admin is None:
        raise HTTPException(status_code=401, detail="管理员不存在")
    return admin