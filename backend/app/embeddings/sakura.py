import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config import get_settings


class SakuraEmbeddings:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.ai_engine_api_base or not settings.ai_engine_api_token or not settings.ai_engine_embeddings_model:
            raise RuntimeError("Embedding設定が不足しています。")

        self._base = settings.ai_engine_api_base.rstrip("/")
        self._token = settings.ai_engine_api_token
        self._model = settings.ai_engine_embeddings_model
        self._prefix = settings.ai_engine_embeddings_prefix

    def create_embeddings(self, texts: list[str]) -> list[list[float]]:
        inputs = [f"{self._prefix}{text}" for text in texts]
        body = json.dumps({"model": self._model, "input": inputs}).encode("utf-8")
        url = f"{self._base}/embeddings"
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
            with urlopen(request, timeout=30) as response:
                if response.status >= 300:
                    raise RuntimeError(f"Embedding作成に失敗しました。status={response.status}")
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode("utf-8")
            except Exception:
                detail = ""
            message = f"Embedding作成に失敗しました。status={exc.code}"
            if detail:
                message = f"{message} detail={detail}"
            raise RuntimeError(message) from exc
        except URLError as exc:
            raise RuntimeError("Embedding作成に失敗しました。") from exc

        data = payload.get("data", []) if isinstance(payload, dict) else []
        indexed: dict[int, list[float]] = {}
        for item in data:
            if not isinstance(item, dict):
                continue
            index = item.get("index")
            embedding = item.get("embedding")
            if isinstance(index, int) and isinstance(embedding, list):
                indexed[index] = embedding

        embeddings: list[list[float]] = []
        for index in range(len(inputs)):
            if index not in indexed:
                raise RuntimeError("Embeddingのレスポンスが不正です。")
            embeddings.append(indexed[index])
        return embeddings
