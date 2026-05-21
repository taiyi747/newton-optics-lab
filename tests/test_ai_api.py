import json
import unittest

from lib.api import ai as ai_api
from lib.ai_module import API_ERROR_PREFIX


class TestAISSEFormatting(unittest.TestCase):
    def test_openai_content_chunk_shape(self):
        payload = ai_api._openai_content_chunk("你好")

        self.assertEqual(payload["choices"][0]["delta"]["content"], "你好")
        self.assertIsNone(payload["choices"][0]["finish_reason"])

    def test_sse_data_uses_data_frame(self):
        frame = ai_api._sse_data(ai_api._openai_content_chunk("你好"))

        self.assertTrue(frame.startswith("data: "))
        self.assertTrue(frame.endswith("\n\n"))
        parsed = json.loads(frame.removeprefix("data: ").strip())
        self.assertEqual(parsed["choices"][0]["delta"]["content"], "你好")

    def test_openai_error_chunk_keeps_visible_error_text(self):
        payload = ai_api._openai_error_chunk("timeout")

        self.assertEqual(payload["choices"][0]["finish_reason"], "error")
        self.assertEqual(
            payload["choices"][0]["delta"]["content"],
            f"{API_ERROR_PREFIX}timeout",
        )


if __name__ == "__main__":
    unittest.main()
