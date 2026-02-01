import unittest
from unittest.mock import MagicMock, patch

from app.repositories.chunks import create_chunk, search_chunks


class TestChunksRepository(unittest.TestCase):
    @patch("app.repositories.chunks.get_connection")
    def test_create_chunk(self, mock_get_connection: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        create_chunk(
            doc_id=1,
            uuid="chunk-uuid",
            chunk_index=1,
            content="text",
            page_start=1,
            page_end=1,
            embedding=[0.1, 0.2],
        )

        mock_cursor.execute.assert_called_once()

    @patch("app.repositories.chunks.get_connection")
    def test_search_chunks(self, mock_get_connection: MagicMock) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"doc_id": 1, "page_start": 1, "page_end": 1, "content": "text", "distance": 0.1}
        ]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value.__enter__.return_value = mock_conn

        results = search_chunks([0.1, 0.2], limit=5)

        self.assertEqual(len(results), 1)
        mock_cursor.execute.assert_called_once()
