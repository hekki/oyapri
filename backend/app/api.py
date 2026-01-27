from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import get_settings
from app.domain.documents import new_doc_id, originals_object_key
from app.storage.s3 import S3Storage

router = APIRouter(prefix="/api/v1")


@router.put("/uploads")
async def upload_pdf(file: UploadFile = File(...)) -> dict:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="PDFのみ対応しています。")

    settings = get_settings()
    if not settings.s3_bucket:
        raise HTTPException(status_code=500, detail="S3設定が不足しています。")

    doc_id = new_doc_id()
    object_key = originals_object_key(doc_id)

    storage = S3Storage(settings)
    storage.upload_pdf(object_key, file.file)

    return {
        "doc_id": doc_id,
        "object_key": object_key,
        "bucket": settings.s3_bucket,
    }
