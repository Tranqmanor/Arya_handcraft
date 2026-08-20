"""Arya 智能助手核心逻辑:对话、记忆、意图识别。"""
import re
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AiMessage
from app.services.llm import LLMClient, LLMError, get_llm_client

# 系统提示词(来源 docs/arya-prompt.md §1)
SYSTEM_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "docs"
    / "arya-prompt.md"
)

HISTORY_LIMIT = 20

# 意图兜底关键词(见 arya-prompt §2)
CALL_MASTER_KEYWORDS = [
    "价格",
    "多少钱",
    "怎么买",
    "下单",
    "定制",
    "购买",
    "预订",
    "预约",
    "想做一个",
    "帮我做",
    "询价",
    "报价",
    "多少钱",
]


def _system_prompt() -> str:
    """读取 docs/arya-prompt.md 的 §1 系统提示词(截取至「## 2」)。"""
    try:
        text = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        # 取 ```text 代码块内容
        m = re.search(r"```text\n(.*?)\n```", text, re.DOTALL)
        return m.group(1).strip() if m else text
    except FileNotFoundError:
        # 兜底内联提示词
        return (
            "你是「Arya」,毛毡手作工作室 Arya_handcraft 的 AI 助手,温柔耐心。"
            "客户有购买/定制/询价意向时必须唤起呼叫主人。"
            '输出 JSON:{"intent":"call_master|info|smalltalk","call_master_hint":"","reply":"回复"}'
        )


def load_recent_history(db: Session, user_id: int, limit: int = HISTORY_LIMIT) -> list[AiMessage]:
    stmt = (
        select(AiMessage)
        .where(AiMessage.user_id == user_id)
        .order_by(AiMessage.id.asc())
    )
    rows = list(db.scalars(stmt).all())
    return rows[-limit:]


def _fallback_intent(user_message: str) -> bool:
    """关键词兜底:命中购买意向即需呼叫主人。"""
    return any(k in user_message for k in CALL_MASTER_KEYWORDS)


def _build_messages(user_message: str, history: list[AiMessage]) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = [{"role": "system", "content": _system_prompt()}]
    # 记忆(history 已含最新 up to N 条;避免与本次 user 重复,故只取 assistant+user 对)
    for m in history:
        if m.role in ("user", "assistant"):
            messages.append({"role": m.role, "content": m.content})
    messages.append({"role": "user", "content": user_message})
    return messages


def _safe_parse(raw: dict, user_message: str, llm_failed: bool = False) -> dict:
    """解析/兜底 LLM 输出,intent 判断 + call_master 强制兜底。"""
    intent = raw.get("intent", "smalltalk")
    reply = raw.get("reply") or "喵~ 收到你的消息啦,我还在学习中。"
    call_master_hint = raw.get("call_master_hint") or ""

    if intent not in ("call_master", "info", "smalltalk"):
        intent = "smalltalk"

    # 关键兜底:命中购买意向关键词而 LLM 未唤起 → 强制
    if _fallback_intent(user_message) and intent != "call_master":
        intent = "call_master"

    if intent == "call_master" and not call_master_hint:
        call_master_hint = "点击下方按钮,添加店主微信咨询吧~"
    if intent != "call_master":
        call_master_hint = ""
    return {"intent": intent, "reply": reply, "call_master_hint": call_master_hint}


async def chat(
    db: Session,
    user_id: int,
    user_message: str,
    llm: LLMClient | None = None,
) -> dict:
    """处理一次对话:入库 → 调 LLM → 兜底 → 回复入库。"""
    # 保存用户消息
    user_msg = AiMessage(user_id=user_id, role="user", content=user_message, intent=None)
    db.add(user_msg)
    db.flush()

    history = load_recent_history(db, user_id)
    history = [m for m in history if m.id != user_msg.id]  # 排除刚插入的自身

    client = llm or get_llm_client()
    raw: dict = {}
    llm_failed = False
    if client is None:
        llm_failed = True
    else:
        try:
            raw = await client.chat_json(_build_messages(user_message, history))
        except LLMError:
            llm_failed = True

    result = _safe_parse(raw, user_message, llm_failed=llm_failed)

    # 保存助手回复
    assistant_msg = AiMessage(
        user_id=user_id,
        role="assistant",
        content=result["reply"],
        intent=result["intent"],
    )
    db.add(assistant_msg)
    db.commit()
    return result