import unittest
from unittest.mock import MagicMock, patch

from app.worker.ingest import process_ingest_job


class TestWorkerIngest(unittest.TestCase):
    @patch("app.worker.ingest.upsert_document_page")
    @patch("app.worker.ingest.TesseractOCR")
    @patch("app.worker.ingest.S3Storage")
    @patch("app.worker.ingest.get_document")
    @patch("app.worker.ingest.get_ingest_job")
    @patch("app.worker.ingest.mark_ingest_job_processing")
    @patch("app.worker.ingest.mark_ingest_job_done")
    @patch("app.worker.ingest.update_document_status")
    @patch("app.worker.ingest._list_original_image_keys")
    def test_process_ingest_job_success(
        self,
        mock_list_keys: MagicMock,
        mock_update_doc_status: MagicMock,
        mock_mark_done: MagicMock,
        mock_mark_processing: MagicMock,
        mock_get_job: MagicMock,
        mock_get_doc: MagicMock,
        mock_storage: MagicMock,
        mock_ocr_cls: MagicMock,
        mock_upsert_page: MagicMock,
    ) -> None:
        mock_get_job.return_value = {"id": 1, "doc_id": 10, "attempts": 0}
        mock_get_doc.return_value = {"id": 10, "uuid": "doc-uuid", "status": "pending"}
        mock_list_keys.return_value = [(1, "originals/doc-uuid.png")]

        storage_instance = MagicMock()
        storage_instance.download_bytes.return_value = b"image"
        mock_storage.return_value = storage_instance

        ocr_instance = MagicMock()
        ocr_instance.extract_text.return_value = "text"
        mock_ocr_cls.return_value = ocr_instance

        process_ingest_job(1)

        mock_mark_processing.assert_called_once()
        mock_upsert_page.assert_called_once()
        storage_instance.upload_text.assert_called_once()
        mock_mark_done.assert_called_once()
        mock_update_doc_status.assert_any_call(10, "processing")
        mock_update_doc_status.assert_any_call(10, "done")
