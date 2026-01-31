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


def get_ingest_job(job_id: int) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, doc_id, status, attempts
                FROM ingest_jobs
                WHERE id = %s
                """,
                (job_id,),
            )
            return cur.fetchone()


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


def mark_ingest_job_processing(job_id: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE ingest_jobs
                SET status = %s, started_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                ("processing", job_id),
            )


def mark_ingest_job_done(job_id: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE ingest_jobs
                SET status = %s, finished_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                ("done", job_id),
            )


def mark_ingest_job_failed(job_id: int, last_error: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE ingest_jobs
                SET status = %s,
                    last_error = %s,
                    attempts = attempts + 1,
                    finished_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                ("failed", last_error, job_id),
            )
