"""进程内滑动窗口限流(轻量防刷)。

适用于当前单实例部署(Railway/单 uvicorn worker);
若未来多实例部署,可将本模块替换为 Redis INCR+EXPIRE 实现,接口保持不变。
"""
import time
from collections import defaultdict, deque

from fastapi import Request

# key -> 窗口内的请求时间戳队列
_BUCKETS: dict[str, deque[float]] = defaultdict(deque)

# 桶总数上限(防御内存膨胀:被恶意构造大量不同 key 时清空重来,仅短暂损失限流精度)
_MAX_BUCKETS = 100_000


def allow(key: str, limit: int, window_seconds: float) -> bool:
    """滑动窗口计数:window_seconds 内最多允许 limit 次;超出返回 False。"""
    if len(_BUCKETS) > _MAX_BUCKETS:
        _BUCKETS.clear()

    now = time.monotonic()
    bucket = _BUCKETS[key]

    # 弹出滑出窗口的过期记录
    while bucket and now - bucket[0] > window_seconds:
        bucket.popleft()

    if len(bucket) >= limit:
        return False

    bucket.append(now)
    return True


def client_ip(request: Request) -> str:
    """取客户端真实 IP(反向代理场景优先解析 X-Forwarded-For 第一段)。"""
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def reset() -> None:
    """清空全部计数(仅供测试隔离使用)。"""
    _BUCKETS.clear()
