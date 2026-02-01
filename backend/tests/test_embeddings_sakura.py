import json
import unittest
from unittest.mock import MagicMock, patch

from app.embeddings.sakura import SakuraEmbeddings


class TestSakuraEmbeddings(unittest.TestCase):
    @patch("app.embeddings.sakura.urlopen")
    @patch("app.embeddings.sakura.get_settings")
    def test_create_embeddings_success(self, mock_settings: MagicMock, mock_urlopen: MagicMock) -> None:
        mock_settings.return_value.ai_engine_api_base = "https://api.ai.sakura.ad.jp/v1"
        mock_settings.return_value.ai_engine_api_token = "token"
        mock_settings.return_value.ai_engine_embeddings_model = "multilingual-e5-large"
        mock_settings.return_value.ai_engine_embeddings_prefix = "passage: "
        mock_settings.return_value.ai_engine_query_prefix = "query: "
        mock_settings.return_value.ai_engine_chat_model = "chat-model"

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(
            {"data": [{"index": 0, "embedding": [0.1, 0.2]}]}
        ).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = SakuraEmbeddings()
        embeddings = client.create_embeddings(["テスト"])

        self.assertEqual(embeddings, [[0.1, 0.2]])

    @patch("app.embeddings.sakura.urlopen")
    @patch("app.embeddings.sakura.get_settings")
    def test_create_query_embedding(self, mock_settings: MagicMock, mock_urlopen: MagicMock) -> None:
        mock_settings.return_value.ai_engine_api_base = "https://api.ai.sakura.ad.jp/v1"
        mock_settings.return_value.ai_engine_api_token = "token"
        mock_settings.return_value.ai_engine_embeddings_model = "multilingual-e5-large"
        mock_settings.return_value.ai_engine_embeddings_prefix = "passage: "
        mock_settings.return_value.ai_engine_query_prefix = "query: "
        mock_settings.return_value.ai_engine_chat_model = "chat-model"

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(
            {"data": [{"index": 0, "embedding": [0.3, 0.4]}]}
        ).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = SakuraEmbeddings()
        embedding = client.create_query_embedding("検索")

        self.assertEqual(embedding, [0.3, 0.4])
