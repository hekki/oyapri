from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import get_settings
from app.domain.documents import new_doc_id, originals_object_key
from app.queue.simplemq import SimpleMQQueue
from app.repositories.documents import create_document, update_document_status
from app.repositories.ingest_jobs import create_ingest_job, update_ingest_job_status
from app.storage.s3 import S3Storage

router = APIRouter(prefix="/api/v1")


@router.put("/uploads")
async def upload_pdf(file: UploadFile = File(...)) -> dict:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="PDFのみ対応しています。")

    settings = get_settings()
    if not settings.s3_bucket:
        raise HTTPException(status_code=500, detail="S3設定が不足しています。")

    doc_uuid = new_doc_id()
    object_key = originals_object_key(doc_uuid)

    doc_id = create_document(
        uuid=doc_uuid,
        status="pending",
        original_filename=file.filename,
    )

    storage = S3Storage(settings)
    try:
        storage.upload_pdf(object_key, file.file)
    except Exception:
        update_document_status(doc_id, "failed")
        raise

    job_uuid = new_doc_id()
    job_id = create_ingest_job(doc_id=doc_id, uuid=job_uuid, status="queued")
    try:
        queue = SimpleMQQueue()
        queue.send_ingest_job(job_id)
    except Exception as exc:
        update_ingest_job_status(job_id, "failed", str(exc))
        update_document_status(doc_id, "failed")
        raise

    return {
        "doc_id": doc_id,
        "doc_uuid": doc_uuid,
        "job_id": job_id,
        "object_key": object_key,
        "bucket": settings.s3_bucket,
    }
