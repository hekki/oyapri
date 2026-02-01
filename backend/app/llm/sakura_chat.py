import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config import get_settings


class SakuraChat:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.ai_engine_api_base or not settings.ai_engine_api_token or not settings.ai_engine_chat_model:
            raise RuntimeError("LLM設定が不足しています。")
        self._base = settings.ai_engine_api_base.rstrip("/")
        self._token = settings.ai_engine_api_token
        self._model = settings.ai_engine_chat_model

    def create_answer(self, system: str, user: str) -> str:
        body = json.dumps(
            {
                "model": self._model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.0,
            }
        ).encode("utf-8")
        url = f"{self._base}/chat/completions"
        request = Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=60) as response:
                if response.status >= 300:
                    raise RuntimeError(f"回答生成に失敗しました。status={response.status}")
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode("utf-8")
            except Exception:
                detail = ""
            message = f"回答生成に失敗しました。status={exc.code}"
            if detail:
                message = f"{message} detail={detail}"
            raise RuntimeError(message) from exc
        except URLError as exc:
            raise RuntimeError("回答生成に失敗しました。") from exc

        choices = payload.get("choices", []) if isinstance(payload, dict) else []
        if not choices:
            raise RuntimeError("回答生成に失敗しました。")
        message = choices[0].get("message", {})
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("回答生成に失敗しました。")
        return content.strip()
