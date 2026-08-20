from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models import User
from app.schemas.coupon import CouponOut
from app.schemas.user import UserOut, UserUpdate
from app.services.coupon import list_user_coupons

router = APIRouter(prefix="/users", tags=["users"])


def get_current_user(authorization: str, db: Session) -> User:
    """从 Authorization header 解析当前用户。"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization.removeprefix("Bearer ").strip()
    subject = decode_token(token, expected_type="access")
    if subject is None:
        raise HTTPException(status_code=401, detail="token 无效或已过期")
    user = db.get(User, int(subject))
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


async def get_current_user_dep(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI 依赖:可直接注入到接口获取当前用户。"""
    return get_current_user(authorization, db)


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user_dep)):
    return current_user


@router.put("/me", response_model=UserOut)
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    if payload.nickname is not None:
        current_user.nickname = payload.nickname
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url
    if payload.phone is not None:
        current_user.phone = payload.phone
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/coupons", response_model=list[CouponOut])
def read_my_coupons(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    return list_user_coupons(db, current_user.id)