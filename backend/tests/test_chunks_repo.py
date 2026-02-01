import unittest
from unittest.mock import MagicMock, patch

from app.repositories.chunks import create_chunk


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
