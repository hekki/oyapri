from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.config import get_settings
from app.domain.documents import new_doc_id, originals_object_key
from app.embeddings import SakuraEmbeddings
from app.llm import SakuraChat
from app.queue.simplemq import SimpleMQQueue
from app.repositories.chunks import search_chunks
from app.repositories.documents import create_document, update_document_status
from app.repositories.ingest_jobs import create_ingest_job, update_ingest_job_status
from app.storage.s3 import S3Storage

router = APIRouter(prefix="/api/v1")


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


@router.put("/")
async def upload_images(files: list[UploadFile] = File(...)) -> dict:
    if not files:
        raise HTTPException(status_code=400, detail="画像を選択してください。")

    settings = get_settings()
    if not settings.s3_bucket:
        raise HTTPException(status_code=500, detail="S3設定が不足しています。")

    for file in files:
        if not file.content_type or file.content_type not in {"image/png", "image/jpeg"}:
            raise HTTPException(status_code=400, detail="PNG/JPEGのみ対応しています。")

    doc_uuid = new_doc_id()
    object_keys: list[str] = []

    doc_id = create_document(
        uuid=doc_uuid,
        status="pending",
        original_filename=files[0].filename if files else None,
    )

    storage = S3Storage(settings)
    try:
        for index, file in enumerate(files, start=1):
            content_type = file.content_type or ""
            ext = "png" if content_type == "image/png" else "jpg"
            page_no = None if len(files) == 1 else index
            object_key = originals_object_key(doc_uuid, ext, page_no)
            storage.upload_image(object_key, file.file, content_type)
            object_keys.append(object_key)
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
        "object_keys": object_keys,
        "bucket": settings.s3_bucket,
    }


@router.post("/search")
async def search_documents(request: SearchRequest) -> dict:
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="検索クエリを入力してください。")

    embeddings = SakuraEmbeddings()
    query_embedding = embeddings.create_query_embedding(query)
    results = search_chunks(query_embedding, max(1, min(request.top_k, 20)))
    return {
        "query": query,
        "results": results,
    }


class AskRequest(BaseModel):
    question: str
    top_k: int = 3


@router.post("/ask")
async def ask_documents(request: AskRequest) -> dict:
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="質問を入力してください。")

    embeddings = SakuraEmbeddings()
    query_embedding = embeddings.create_query_embedding(question)
    results = search_chunks(query_embedding, max(1, min(request.top_k, 6)))
    if not results:
        return {
            "answer": "不明です。追加情報を教えてください。",
            "citations": [],
        }

    context_lines: list[str] = []
    citations: list[dict] = []
    for idx, item in enumerate(results, start=1):
        doc_id = item.get("doc_id")
        page_start = item.get("page_start")
        page_end = item.get("page_end")
        content = item.get("content", "")
        snippet = content.strip().replace("\n", " ")
        if len(snippet) > 200:
            snippet = snippet[:200] + "…"
        context_lines.append(
            f"[{idx}] doc_id={doc_id} page={page_start}-{page_end}\n{snippet}"
        )
        citations.append(
            {
                "doc_id": doc_id,
                "page_start": page_start,
                "page_end": page_end,
                "quote": "",
            }
        )

    system = (
        "あなたは教材プリントの内容に基づいて回答するアシスタントです。"
        "与えられた根拠以外の推測はせず、不明な場合は「不明」と答えて追加情報を求めてください。"
        "回答は日本語で簡潔に、60文字以内を目安に。"
        "同じ内容の繰り返しは避け、箇条書きは最大2件まで。"
        "読みやすさを最優先し、必要なら改行・箇条書き・太字・表を使って整形してください。"
    )
    user = (
        "以下の根拠に基づいて質問に答えてください。\n"
        "根拠:\n"
        + "\n\n".join(context_lines)
        + "\n\n質問:\n"
        + question
    )

    chat = SakuraChat()
    answer = chat.create_answer(system=system, user=user)
    return {
        "answer": answer,
        "citations": citations,
    }
