"""Arya 智能助手测试(mock LLM,不依赖外部网络)。"""
from unittest.mock import AsyncMock, patch

from app.core.security import create_access_token
from app.models import AiMessage, User
from app.services.arya import _fallback_intent


def _auth_headers(user_id: int) -> dict:
    return {"Authorization": f"Bearer {create_access_token(str(user_id))}"}


def _mk_user(db) -> User:
    user = User(openid="openid-arya-1", nickname="", avatar_url="", phone=None)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_arya_requires_auth(client):
    resp = client.post("/api/v1/arya/chat", json={"message": "你好"})
    assert resp.status_code == 401


def test_arya_chat_call_master_intent(client, db_session):
    db = db_session()
    user = _mk_user(db)
    user_id = user.id
    db.close()

    fake_llm = AsyncMock()
    fake_llm.chat_json.return_value = {
        "intent": "call_master",
        "reply": "想定制吗?我帮你呼叫店主~",
        "call_master_hint": "点这里联系店主",
    }

    with patch("app.api.v1.arya.get_llm_client", return_value=fake_llm):
        resp = client.post(
            "/api/v1/arya/chat",
            headers=_auth_headers(user_id),
            json={"message": "我想定做一个毛毡猫"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "call_master"
    assert data["call_master_hint"]


def test_arya_chat_info_intent(client, db_session):
    db = db_session()
    user = _mk_user(db)
    user_id = user.id
    db.close()

    fake_llm = AsyncMock()
    fake_llm.chat_json.return_value = {
        "intent": "info",
        "reply": "羊毛毡猫咪可以按照片定制哦~",
        "call_master_hint": "",
    }

    with patch("app.api.v1.arya.get_llm_client", return_value=fake_llm):
        resp = client.post(
            "/api/v1/arya/chat",
            headers=_auth_headers(user_id),
            json={"message": "介绍下你们的手作吧"},
        )

    assert resp.status_code == 200
    assert resp.json()["intent"] == "info"


def test_arya_fallback_keyword_force_call_master(client, db_session):
    """LLM 误判为 smalltalk,但命中购买关键词 → 后端强制 call_master。"""
    db = db_session()
    user = _mk_user(db)
    user_id = user.id
    db.close()

    fake_llm = AsyncMock()
    fake_llm.chat_json.return_value = {
        "intent": "smalltalk",
        "reply": "你家的猫咪真可爱呀~",
        "call_master_hint": "",
    }

    with patch("app.api.v1.arya.get_llm_client", return_value=fake_llm):
        resp = client.post(
            "/api/v1/arya/chat",
            headers=_auth_headers(user_id),
            json={"message": "我想问问定制要多少钱"},
        )

    assert resp.json()["intent"] == "call_master"
    assert resp.json()["call_master_hint"]


def test_arya_memory_persists(client, db_session):
    """对话历史应入库,清空接口可用。"""
    db = db_session()
    user = _mk_user(db)
    user_id = user.id
    db.close()

    fake_llm = AsyncMock()
    fake_llm.chat_json.return_value = {
        "intent": "smalltalk",
        "reply": "喵,我在的~",
        "call_master_hint": "",
    }

    with patch("app.api.v1.arya.get_llm_client", return_value=fake_llm):
        client.post(
            "/api/v1/arya/chat",
            headers=_auth_headers(user_id),
            json={"message": "喵你好"},
        )
    # 共 2 条(user + assistant)
    db2 = db_session()
    messages = db2.query(AiMessage).filter(AiMessage.user_id == user_id).all()
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"
    # 清空
    resp = client.delete("/api/v1/arya/sessions", headers=_auth_headers(user_id))
    assert resp.status_code == 200
    assert db2.query(AiMessage).filter(AiMessage.user_id == user_id).count() == 0
    db2.close()


def test_fallback_intent():
    assert _fallback_intent("多少钱") is True
    assert _fallback_intent("怎么定制") is True
    assert _fallback_intent("你好呀") is False