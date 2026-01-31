from app.db import get_connection


def create_document(uuid: str, status: str, original_filename: str | None) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO documents (uuid, status, original_filename)
                VALUES (%s, %s, %s)
                """,
                (uuid, status, original_filename),
            )
            return int(cur.lastrowid)


def update_document_status(doc_id: int, status: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE documents
                SET status = %s
                WHERE id = %s
                """,
                (status, doc_id),
            )


def get_document(doc_id: int) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, uuid, status
                FROM documents
                WHERE id = %s
                """,
                (doc_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            if isinstance(row, dict):
                return row
            return {"id": row[0], "uuid": row[1], "status": row[2]}
