import unittest
from unittest.mock import MagicMock, patch

from app.repositories.documents import create_document, update_document_status


class TestDocumentsRepository(unittest.TestCase):
    @patch("app.repositories.documents.get_connection")
    def test_create_document(self, mock_get_connection: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 42
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        doc_id = create_document(
            uuid="test-uuid",
            status="pending",
            original_filename="sample.pdf",
        )

        self.assertEqual(doc_id, 42)
        mock_cursor.execute.assert_called_once()

    @patch("app.repositories.documents.get_connection")
    def test_update_document_status(self, mock_get_connection: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        update_document_status(doc_id=7, status="failed")

        mock_cursor.execute.assert_called_once()
