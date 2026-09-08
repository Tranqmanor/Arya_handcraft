"""用户级图片上传(下单时的猫咪图片等),限流防滥用。"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.v1.users import get_current_user_dep
from app.core import ratelimit
from app.db.session import get_db
from app.models import User
from app.services import storage

router = APIRouter(prefix="/user/uploads", tags=["user-uploads"])

# 每用户每小时允许的图片上传次数
UPLOAD_LIMIT = 30


@router.post("/image")
async def user_upload_image(
    file: UploadFile,
    user: User = Depends(get_current_user_dep),
    _db: Session = Depends(get_db),
):
    if not ratelimit.allow(f"uupload:{user.id}", UPLOAD_LIMIT, 3600):
        raise HTTPException(status_code=429, detail="上传过于频繁,请稍后再试")

    ext = storage.detect_image_ext(file.filename)
    if ext is None:
        raise HTTPException(status_code=400, detail="仅支持 jpg/jpeg/png/webp/gif 格式")

    data = await file.read()
    try:
        storage.validate_image(data, ext)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        url = storage.upload_image(data, ext, prefix="uploads/user")
    except storage.UploadError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return {"url": url}
