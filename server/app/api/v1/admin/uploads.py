"""通用文件上传:文章配图/封面(视频通道预留,复用同一服务层)。"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.api.v1.admin.deps import get_current_admin
from app.models import AdminUser
from app.services import storage

router = APIRouter(prefix="/admin/uploads", tags=["admin-uploads"])


@router.post("/image")
async def admin_upload_image(
    file: UploadFile,
    _admin: AdminUser = Depends(get_current_admin),
):
    """上传图片并返回公开访问 URL。

    错误码约定:400 文件不合法 / 401 未登录 / 503 对象存储未配置或故障。
    """
    ext = storage.detect_image_ext(file.filename)
    if ext is None:
        raise HTTPException(status_code=400, detail="仅支持 jpg/jpeg/png/webp/gif 格式")

    data = await file.read()
    try:
        storage.validate_image(data, ext)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        url = storage.upload_image(data, ext)
    except storage.UploadError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return {"url": url}

