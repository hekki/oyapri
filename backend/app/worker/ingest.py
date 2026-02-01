import logging
import sys

from app.config import get_settings
from app.domain.documents import new_doc_id, ocr_text_object_key
from app.embeddings import SakuraEmbeddings
from app.ocr import TesseractOCR
from app.repositories.chunks import create_chunk
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


def _split_by_chars(text: str, size: int, overlap: int) -> list[str]:
    if size <= 0:
        return [text] if text else []
    if overlap < 0:
        overlap = 0
    if overlap >= size:
        overlap = max(size - 1, 0)

    chunks: list[str] = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + size, length)
        chunk = text[start:end]
        if chunk:
            chunks.append(chunk)
        if end == length:
            break
        start = end - overlap
    return chunks


def _cap_chunks_by_max_chars(chunks: list[tuple[int, str]], max_chars: int) -> list[tuple[int, str]]:
    if max_chars <= 0:
        return chunks
    capped: list[tuple[int, str]] = []
    for page_no, text in chunks:
        if len(text) <= max_chars:
            capped.append((page_no, text))
            continue
        for sub in _split_by_chars(text, max_chars, 0):
            capped.append((page_no, sub))
    return capped


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
    embeddings = SakuraEmbeddings()

    try:
        page_items = _list_original_image_keys(storage, doc["uuid"])
        if not page_items:
            raise RuntimeError("原本画像が見つかりません。")

        page_texts: list[tuple[int, str]] = []
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
            page_texts.append((page_no, text))

        chunk_texts: list[tuple[int, str]] = []
        for page_no, text in page_texts:
            for chunk in _split_by_chars(text, settings.chunk_size, settings.chunk_overlap):
                chunk_texts.append((page_no, chunk))

        max_chars = int(settings.embedding_max_tokens * settings.embedding_chars_per_token)
        chunk_texts = _cap_chunks_by_max_chars(chunk_texts, max_chars)

        if chunk_texts:
            embeddings_list = embeddings.create_embeddings([text for _, text in chunk_texts])
            if len(embeddings_list) != len(chunk_texts):
                raise RuntimeError("Embedding件数が一致しません。")

            chunk_index = 1
            for (page_no, text), embedding in zip(chunk_texts, embeddings_list, strict=False):
                create_chunk(
                    doc_id=doc["id"],
                    uuid=new_doc_id(),
                    chunk_index=chunk_index,
                    content=text,
                    page_start=page_no,
                    page_end=page_no,
                    embedding=embedding,
                )
                chunk_index += 1

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
