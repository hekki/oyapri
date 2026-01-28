import base64
import json
import unittest
from io import BytesIO
from unittest.mock import MagicMock, patch

from app.queue.simplemq import SimpleMQQueue


class TestSimpleMQQueue(unittest.TestCase):
    @patch("app.queue.simplemq.urlopen")
    @patch("app.queue.simplemq.get_settings")
    def test_send_ingest_job_success(self, mock_settings: MagicMock, mock_urlopen: MagicMock) -> None:
        mock_settings.return_value.simplemq_endpoint = "https://simplemq.example.com"
        mock_settings.return_value.simplemq_queue_name = "oyapri"
        mock_settings.return_value.simplemq_api_token = "token"

        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        queue = SimpleMQQueue()
        queue.send_ingest_job(123)

        args, kwargs = mock_urlopen.call_args
        request = args[0]
        body = request.data
        payload = json.loads(body.decode("utf-8"))
        decoded = base64.b64decode(payload["content"].encode("ascii"))
        self.assertEqual(json.loads(decoded.decode("utf-8")), {"job_id": 123})
        self.assertEqual(request.get_header("Authorization"), "Bearer token")

    @patch("app.queue.simplemq.urlopen")
    @patch("app.queue.simplemq.get_settings")
    def test_send_ingest_job_http_error(self, mock_settings: MagicMock, mock_urlopen: MagicMock) -> None:
        from urllib.error import HTTPError

        mock_settings.return_value.simplemq_endpoint = "https://simplemq.example.com"
        mock_settings.return_value.simplemq_queue_name = "oyapri"
        mock_settings.return_value.simplemq_api_token = "token"

        from email.message import Message

        error_stream = BytesIO(b"")
        http_error = HTTPError(
            url="https://simplemq.example.com",
            code=500,
            msg="error",
            hdrs=Message(),
            fp=error_stream,
        )
        mock_urlopen.side_effect = http_error

        queue = SimpleMQQueue()
        try:
            with self.assertRaises(RuntimeError):
                queue.send_ingest_job(123)
        finally:
            http_error.close()
