"""订单金额与排队规则(单一事实来源:服务层/路由/测试共用)。

阶段金额规则(基于折后总价 = max(0, 定价 - 券面额)):
- 折后总价 >= 1000:排队定金 300;制作定金 = floor10(30% - 300);尾款为余数
- 折后总价 <  1000:排队定金 = floor10(30%);制作定金 0;尾款为余数
- floor10 = 向下取整到十位(如 336.5 → 330)
"""


def _floor10(x: int) -> int:
    return (x // 10) * 10


def settle_amounts(total_price: int, coupon_amount: int = 0) -> tuple[int, int, int]:
    """计算三阶段应付金额,返回 (排队定金, 制作定金, 尾款);三者之和恒等于折后总价。"""
    effective = max(0, int(total_price) - int(coupon_amount))
    if effective >= 1000:
        deposit = 300
        making = _floor10(effective * 3 // 10 - deposit)
    else:
        deposit = _floor10(effective * 3 // 10)
        making = 0
    final = effective - deposit - making
    return deposit, making, final


# 订单状态 → 中文标签
STATUS_LABELS = {
    "pending_price": "待定价",
    "pending_deposit": "待付排队定金",
    "queued": "排队中",
    "pending_making": "待付制作定金",
    "making": "制作中",
    "pending_final": "待付尾款",
    "ready_to_ship": "待寄出",
    "shipped": "已寄出",
    "completed": "已完成",
    "refund_requested": "退款申请中",
    "refunded": "已退款",
    "cancelled": "已关闭",
}

# 占用排队位的状态(交付完成/关闭/退款后释放)
QUEUE_OCCUPYING = frozenset(
    {
        "pending_price",
        "pending_deposit",
        "queued",
        "pending_making",
        "making",
        "pending_final",
        "ready_to_ship",
    }
)

# 客户可申请退款的状态(已付排队定金后、寄出前)
REFUND_REQUESTABLE = frozenset({"queued", "pending_making", "making", "pending_final", "ready_to_ship"})

# 待付排队定金超时(小时):超时未确认到账自动关闭
DEPOSIT_TIMEOUT_HOURS = 24

# 推荐奖励:被邀请订单尾款到账后,给推荐人发的券(元)
REFERRAL_COUPON_TITLE = "推荐好友奖励"
REFERRAL_COUPON_AMOUNT = 50
REFERRAL_COUPON_VALID_DAYS = 90
