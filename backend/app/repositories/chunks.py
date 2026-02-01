import json

from app.db import get_connection


def create_chunk(
    doc_id: int,
    uuid: str,
    chunk_index: int,
    content: str,
    page_start: int,
    page_end: int,
    embedding: list[float],
    token_count: int | None = None,
) -> None:
    embedding_text = json.dumps(embedding, ensure_ascii=False)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chunks (
                    doc_id,
                    uuid,
                    chunk_index,
                    content,
                    page_start,
                    page_end,
                    token_count,
                    embedding
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    doc_id,
                    uuid,
                    chunk_index,
                    content,
                    page_start,
                    page_end,
                    token_count,
                    embedding_text,
                ),
            )


def search_chunks(embedding: list[float], limit: int) -> list[dict]:
    embedding_text = json.dumps(embedding, ensure_ascii=False)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    doc_id,
                    page_start,
                    page_end,
                    content,
                    VEC_COSINE_DISTANCE(embedding, %s) AS distance
                FROM chunks
                ORDER BY distance
                LIMIT %s
                """,
                (embedding_text, limit),
            )
            rows = cur.fetchall()
            return rows if isinstance(rows, list) else []
