from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.db.session import get_db
from app.models import User
from app.schemas.auth import AuthLoginRequest, TokenResponse
from app.services.coupon import grant_new_user_coupon
from app.services.wechat import WechatAuthError, code2session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: AuthLoginRequest, db: Session = Depends(get_db)):
    """微信一键登录:code → openid → 查找/创建用户 → 签发 JWT。"""
    settings = get_settings()
    if not settings.WX_APP_ID or not settings.WX_APP_SECRET:
        raise HTTPException(status_code=500, detail="微信登录未配置(请检查 WX_APP_ID / WX_APP_SECRET)")

    try:
        wx_info = await code2session(payload.code)
    except WechatAuthError as e:
        raise HTTPException(status_code=400, detail=f"微信登录失败: {e.errmsg}") from e

    openid = wx_info["openid"]
    unionid = wx_info.get("unionid")

    user = db.scalar(select(User).where(User.openid == openid))
    created = user is None
    if user is None:
        user = User(openid=openid, unionid=unionid, nickname="", avatar_url="")
        db.add(user)
        db.commit()
        db.refresh(user)
        # 新客自动发券
        grant_new_user_coupon(db, user.id)
    elif unionid and not user.unionid:
        user.unionid = unionid
        db.commit()

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: dict, db: Session = Depends(get_db)):
    """用 refresh_token 换新 token。"""
    refresh_token = payload.get("refresh_token", "")
    subject = decode_token(refresh_token, expected_type="refresh")
    if subject is None:
        raise HTTPException(status_code=401, detail="refresh token 无效或已过期")

    user = db.get(User, int(subject))
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )