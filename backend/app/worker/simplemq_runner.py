import json
import logging
import time

from app.queue.simplemq import SimpleMQQueue
from app.worker.ingest import process_ingest_job


logger = logging.getLogger(__name__)


def _extract_job_id(message: dict) -> int | None:
    decoded = message.get("decoded_content")
    if isinstance(decoded, dict) and isinstance(decoded.get("job_id"), int):
        return decoded["job_id"]
    if isinstance(decoded, dict) and isinstance(decoded.get("job_id"), str) and decoded["job_id"].isdigit():
        return int(decoded["job_id"])
    try:
        raw = message.get("content")
        if isinstance(raw, str):
            payload = json.loads(raw)
            job_id = payload.get("job_id")
            if isinstance(job_id, int):
                return job_id
            if isinstance(job_id, str) and job_id.isdigit():
                return int(job_id)
    except Exception:
        return None
    return None


def run_once() -> int:
    queue = SimpleMQQueue()
    messages = queue.receive_messages()
    logger.info("受信件数=%s", len(messages))
    for message in messages:
        message_id = message.get("id")
        job_id = _extract_job_id(message)
        if not job_id or not message_id:
            logger.warning("メッセージ形式が不正のためスキップしました。")
            continue
        logger.info("取り込み開始 job_id=%s", job_id)
        try:
            process_ingest_job(job_id)
        except Exception:
            logger.exception("取り込み失敗 job_id=%s", job_id)
            continue
        queue.delete_message(str(message_id))
        logger.info("取り込み完了 job_id=%s", job_id)
    return len(messages)


def run_forever(poll_interval_seconds: int = 5) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    while True:
        run_once()
        time.sleep(poll_interval_seconds)


if __name__ == "__main__":
    run_forever()
