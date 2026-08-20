"""DeepSeek(OpenAI 兼容)LLM 服务封装。"""
import json
from typing import Any

import httpx

from app.core.config import get_settings


class LLMError(Exception):
    """大模型调用异常。"""


class LLMClient:
    """轻量 OpenAI 兼容客户端(仅覆盖 chat.completions)。"""

    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._client = httpx.AsyncClient(timeout=60)

    async def chat_json(
        self,
        messages: list[dict[str, str]],
        max_tokens: int = 500,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """调用 chat completions,要求返回 JSON 对象。"""
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        resp = await self._client.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
        )
        if resp.status_code != 200:
            raise LLMError(f"LLM 请求失败: HTTP {resp.status_code} {resp.text[:200]}")

        content = resp.json()["choices"][0]["message"]["content"]
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise LLMError(f"LLM 输出非合法 JSON: {content[:200]}") from e

    async def close(self) -> None:
        await self._client.aclose()


def get_llm_client() -> LLMClient | None:
    settings = get_settings()
    if not settings.LLM_API_KEY:
        return None
    return LLMClient(
        base_url=settings.LLM_BASE_URL,
        api_key=settings.LLM_API_KEY,
        model=settings.LLM_MODEL,
    )