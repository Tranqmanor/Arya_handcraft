"""对象存储服务(Cloudflare R2,S3 兼容 API)。

用于文章配图/封面等静态资源上传;按扩展名+magic bytes 双重校验。
后续如需支持视频,在此增加视频类型的白名单与大小上限即可复用同一通道。
"""
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import Settings, get_settings

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

# 扩展名 -> magic bytes 校验器(防改后缀伪装)
_IMAGE_MAGIC = {
    "jpg": lambda d: d[:3] == b"\xff\xd8\xff",
    "jpeg": lambda d: d[:3] == b"\xff\xd8\xff",
    "png": lambda d: d[:8] == b"\x89PNG\r\n\x1a\n",
    "gif": lambda d: d[:6] in (b"GIF87a", b"GIF89a"),
    "webp": lambda d: d[:4] == b"RIFF" and len(d) >= 12 and d[8:12] == b"WEBP",
}

_CONTENT_TYPE = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
}


class UploadError(Exception):
    """存储侧失败(R2 未配置/写入出错),由路由层转换为 503。"""


def detect_image_ext(filename: str | None) -> str | None:
    """从文件名解析受支持的图片扩展名;不支持返回 None。"""
    if not filename or "." not in filename:
        return None
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext if ext in _IMAGE_MAGIC else None


def validate_image(data: bytes, ext: str) -> None:
    """校验图片内容;不合法抛 ValueError(路由层转 400)。"""
    if not data:
        raise ValueError("文件内容为空")
    if len(data) > MAX_IMAGE_SIZE:
        raise ValueError("图片不能超过 10MB")
    if not _IMAGE_MAGIC[ext](data):
        raise ValueError("文件内容与扩展名不符")


def r2_configured(settings: Settings | None = None) -> bool:
    """R2 五项配置是否齐全。"""
    s = settings or get_settings()
    return all(
        (
            s.R2_ACCOUNT_ID,
            s.R2_ACCESS_KEY_ID,
            s.R2_SECRET_ACCESS_KEY,
            s.R2_BUCKET_NAME,
            s.R2_PUBLIC_BASE_URL,
        )
    )


def upload_image(data: bytes, ext: str, settings: Settings | None = None) -> str:
    """上传图片到 R2 并返回公开访问 URL;配置缺失或远端失败抛 UploadError。

    存储键按年月分目录 + uuid,文件名不可预测且天然去重;
    设置一年不可变缓存(CDN 友好)。
    """
    s = settings or get_settings()
    if not r2_configured(s):
        raise UploadError("对象存储未配置(R2_* 环境变量缺失)")

    now = datetime.now(timezone.utc)
    key = f"uploads/{now:%Y%m}/{uuid.uuid4().hex}.{ext}"
    client = boto3.client(
        "s3",
        endpoint_url=f"https://{s.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=s.R2_ACCESS_KEY_ID,
        aws_secret_access_key=s.R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )
    try:
        client.put_object(
            Bucket=s.R2_BUCKET_NAME,
            Key=key,
            Body=data,
            ContentType=_CONTENT_TYPE[ext],
            CacheControl="public, max-age=31536000, immutable",
        )
    except (BotoCoreError, ClientError) as exc:
        raise UploadError(f"对象存储写入失败: {exc}") from exc

    return f"{s.R2_PUBLIC_BASE_URL.rstrip('/')}/{key}"

