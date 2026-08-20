from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.core.config import get_settings

# 微信 code2session 接口
_WX_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


class WechatAuthError(Exception):
    """微信登录接口异常。"""

    def __init__(self, errcode: int, errmsg: str) -> None:
        self.errcode = errcode
        self.errmsg = errmsg
        super().__init__(f"wechat auth error {errcode}: {errmsg}")


async def code2session(code: str) -> dict[str, Any]:
    """用前端 wx.login 的 code 换取 openid/session_key/unionid。"""
    settings = get_settings()
    params = {
        "appid": settings.WX_APP_ID,
        "secret": settings.WX_APP_SECRET,
        "js_code": code,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(_WX_CODE2SESSION_URL, params=params)
        data = resp.json()

    if data.get("errcode"):
        raise WechatAuthError(errmsg=data.get("errmsg", "unknown"), errcode=data.get("errcode"))
    return data