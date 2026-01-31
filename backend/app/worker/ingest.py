import logging
import sys

from app.config import get_settings
from app.domain.documents import new_doc_id, ocr_text_object_key
from app.ocr import TesseractOCR
from app.repositories.document_pages import upsert_document_page
from app.repositories.documents import get_document, update_document_status
from app.repositories.ingest_jobs import (
    get_ingest_job,
    mark_ingest_job_done,
    mark_ingest_job_failed,
    mark_ingest_job_processing,
)
from app.storage.s3 import S3Storage


logger = logging.getLogger(__name__)


def _list_original_image_keys(storage: S3Storage, doc_uuid: str) -> list[tuple[int, str]]:
    page_prefix = f"originals/{doc_uuid}/pages/"
    page_keys = storage.list_keys(page_prefix)
    if page_keys:
        items: list[tuple[int, str]] = []
        for key in page_keys:
            filename = key.split("/")[-1]
            page_str = filename.split(".")[0]
            if page_str.isdigit():
                items.append((int(page_str), key))
        return sorted(items, key=lambda item: item[0])

    single_keys = storage.list_keys(f"originals/{doc_uuid}.")
    for key in single_keys:
        return [(1, key)]
    return []


def process_ingest_job(job_id: int) -> None:
    job = get_ingest_job(job_id)
    if not job:
        raise RuntimeError("ジョブが見つかりません。")
    if job.get("attempts", 0) >= 5:
        return

    logger.info("ジョブ処理開始 job_id=%s", job_id)
    mark_ingest_job_processing(job_id)

    doc = get_document(job["doc_id"])
    if not doc:
        mark_ingest_job_failed(job_id, "ドキュメントが見つかりません。")
        return

    update_document_status(doc["id"], "processing")

    settings = get_settings()
    storage = S3Storage(settings)
    ocr = TesseractOCR(lang=settings.ocr_lang)

    try:
        page_items = _list_original_image_keys(storage, doc["uuid"])
        if not page_items:
            raise RuntimeError("原本画像が見つかりません。")

        for page_no, key in page_items:
            logger.info("OCR処理 page_no=%s key=%s", page_no, key)
            image_bytes = storage.download_bytes(key)
            text = ocr.extract_text(image_bytes)
            storage.upload_text(ocr_text_object_key(doc["uuid"], page_no), text)
            upsert_document_page(
                doc_id=doc["id"],
                page_no=page_no,
                uuid=new_doc_id(),
                text_source="ocr",
                char_count=len(text),
            )

        mark_ingest_job_done(job_id)
        update_document_status(doc["id"], "done")
        logger.info("ジョブ処理完了 job_id=%s", job_id)
    except Exception as exc:
        mark_ingest_job_failed(job_id, str(exc))
        update_document_status(doc["id"], "failed")
        logger.exception("ジョブ処理失敗 job_id=%s", job_id)
        raise


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python -m app.worker.ingest <job_id>")
        return 1
    process_ingest_job(int(sys.argv[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
