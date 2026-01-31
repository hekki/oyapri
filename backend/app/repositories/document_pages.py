from app.db import get_connection


def upsert_document_page(
    doc_id: int,
    page_no: int,
    uuid: str,
    text_source: str,
    char_count: int,
) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO document_pages (doc_id, page_no, uuid, text_source, char_count)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    text_source = VALUES(text_source),
                    char_count = VALUES(char_count),
                    updated_at = CURRENT_TIMESTAMP
                """,
                (doc_id, page_no, uuid, text_source, char_count),
            )
