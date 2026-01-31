import unittest
from unittest.mock import MagicMock, patch

from app.repositories.document_pages import upsert_document_page


class TestDocumentPagesRepository(unittest.TestCase):
    @patch("app.repositories.document_pages.get_connection")
    def test_upsert_document_page(self, mock_get_connection: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        upsert_document_page(
            doc_id=3,
            page_no=1,
            uuid="page-uuid",
            text_source="ocr",
            char_count=120,
        )

        mock_cursor.execute.assert_called_once()
