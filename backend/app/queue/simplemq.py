import base64
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config import get_settings


class SimpleMQQueue:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.simplemq_endpoint or not settings.simplemq_queue_name or not settings.simplemq_api_token:
            raise RuntimeError("キュー設定が不足しています。")

        self._endpoint = settings.simplemq_endpoint.rstrip("/")
        self._queue_name = settings.simplemq_queue_name
        self._api_token = settings.simplemq_api_token

    def send_ingest_job(self, job_id: int) -> None:
        payload = json.dumps({"job_id": job_id}).encode("utf-8")
        body = json.dumps({"content": base64.b64encode(payload).decode("ascii")}).encode("utf-8")
        url = f"{self._endpoint}/v1/queues/{self._queue_name}/messages"
        request = Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {self._api_token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=10) as response:
                if response.status >= 300:
                    raise RuntimeError(f"キュー送信に失敗しました。status={response.status}")
        except HTTPError as exc:
            raise RuntimeError(f"キュー送信に失敗しました。status={exc.code}") from exc
        except URLError as exc:
            raise RuntimeError("キュー送信に失敗しました。") from exc
