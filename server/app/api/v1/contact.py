from fastapi import APIRouter

from app.core.config import get_settings
from pydantic import BaseModel


class ContactConfigOut(BaseModel):
    """联系店主信息(二维码图片 + 提示文案)。"""

    qr_url: str
    tip: str = "长按识别二维码,添加店主微信~"
    nickname: str = "Arya 手作毛毡"


router = APIRouter(prefix="/contact", tags=["contact"])

# 默认二维码部署在小程序 static 下,由前端本地展示;此接口保留轻量扩展能力(如自定义文案)
# 若后续二维码改存 CDN,可在 settings 增加 CONTACT_QR_URL 环境变量。


@router.get("/config", response_model=ContactConfigOut)
def contact_config():
    settings = get_settings()
    return ContactConfigOut(
        qr_url=settings.CONTACT_QR_URL if settings.CONTACT_QR_URL else "",
        tip="长按识别二维码,添加店主微信进行咨询",
    )