from app.db import get_connection


def create_ingest_job(doc_id: int, uuid: str, status: str) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ingest_jobs (doc_id, uuid, status, queued_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """,
                (doc_id, uuid, status),
            )
            return int(cur.lastrowid)


def update_ingest_job_status(job_id: int, status: str, last_error: str | None = None) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE ingest_jobs
                SET status = %s, last_error = %s
                WHERE id = %s
                """,
                (status, last_error, job_id),
            )
