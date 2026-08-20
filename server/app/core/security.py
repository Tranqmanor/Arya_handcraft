from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from jose import jwt, JWTError

from app.core.config import get_settings

ALGORITHM = "HS256"
_PBKDF2_ITERATIONS = 200_000


def hash_password(password: str) -> str:
    """PBKDF2 密码哈希,返回 format: pbkdf2$iterations$salt$hash。"""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), _PBKDF2_ITERATIONS
    ).hex()
    return f"pbkdf2${_PBKDF2_ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, iterations, salt, digest = stored.split("$")
        if scheme != "pbkdf2":
            return False
        calc = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt), int(iterations)
        ).hex()
        return secrets.compare_digest(calc, digest)
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str) -> str:
    """签发 access token(短期)。"""
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "type": "access", "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def create_admin_token(subject: str) -> str:
    """签发管理员 token(独立 type: admin)。"""
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(days=1)
    payload = {"sub": subject, "type": "admin", "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """签发 refresh token(长期)。"""
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": subject, "type": "refresh", "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def decode_token(token: str, expected_type: str | None = None) -> str | None:
    """校验并解析 token,返回 subject;失败返回 None。"""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        if expected_type and payload.get("type") != expected_type:
            return None
        sub = payload.get("sub")
        return sub if isinstance(sub, str) else None
    except JWTError:
        return None