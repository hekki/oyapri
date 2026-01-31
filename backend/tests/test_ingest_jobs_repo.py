import unittest
from unittest.mock import MagicMock, patch

from app.repositories.ingest_jobs import create_ingest_job, update_ingest_job_status
from app.repositories.ingest_jobs import mark_ingest_job_failed, mark_ingest_job_processing


class TestIngestJobsRepository(unittest.TestCase):
    @patch("app.repositories.ingest_jobs.get_connection")
    def test_create_ingest_job(self, mock_get_connection: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 101
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        job_id = create_ingest_job(doc_id=7, uuid="job-uuid", status="queued")

        self.assertEqual(job_id, 101)
        mock_cursor.execute.assert_called_once()

    @patch("app.repositories.ingest_jobs.get_connection")
    def test_update_ingest_job_status(self, mock_get_connection: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        update_ingest_job_status(job_id=9, status="failed", last_error="error")

        mock_cursor.execute.assert_called_once()

    @patch("app.repositories.ingest_jobs.get_connection")
    def test_mark_ingest_job_processing(self, mock_get_connection: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        mark_ingest_job_processing(job_id=5)

        mock_cursor.execute.assert_called_once()

    @patch("app.repositories.ingest_jobs.get_connection")
    def test_mark_ingest_job_failed(self, mock_get_connection: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        mark_ingest_job_failed(job_id=6, last_error="error")

        mock_cursor.execute.assert_called_once()
