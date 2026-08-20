from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.api.v1.users import get_current_user_dep
from app.db.session import get_db
from app.models import AiMessage, User
from app.services.arya import chat
from app.services.llm import get_llm_client

router = APIRouter(prefix="/arya", tags=["arya"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    intent: str
    call_master_hint: str = ""


@router.post("/chat", response_model=ChatResponse)
async def arya_chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    """Arya 对话(需登录)。"""
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="消息不能为空")
    if len(message) > 500:
        raise HTTPException(status_code=400, detail="消息过长")

    # 未配置 LLM 时仍兜底回复,不阻塞
    llm = get_llm_client()
    result = await chat(db, current_user.id, message, llm=llm)
    return ChatResponse(**result)


@router.delete("/sessions")
def clear_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    """清空当前用户历史记忆。"""
    db.execute(delete(AiMessage).where(AiMessage.user_id == current_user.id))
    db.commit()
    return {"detail": "已清空对话记忆"}