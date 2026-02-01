import json
import unittest
from unittest.mock import MagicMock, patch

from app.llm.sakura_chat import SakuraChat


class TestSakuraChat(unittest.TestCase):
    @patch("app.llm.sakura_chat.urlopen")
    @patch("app.llm.sakura_chat.get_settings")
    def test_create_answer_success(self, mock_settings: MagicMock, mock_urlopen: MagicMock) -> None:
        mock_settings.return_value.ai_engine_api_base = "https://api.ai.sakura.ad.jp/v1"
        mock_settings.return_value.ai_engine_api_token = "token"
        mock_settings.return_value.ai_engine_chat_model = "chat-model"

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(
            {"choices": [{"message": {"content": "回答"}}]}
        ).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = SakuraChat()
        answer = client.create_answer(system="system", user="user")

        self.assertEqual(answer, "回答")
