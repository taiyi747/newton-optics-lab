import unittest

from lib import ai_module


class _FakeCompletions:
    def __init__(self, stream):
        self._stream = stream
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return self._stream


class _FakeChat:
    def __init__(self, stream):
        self.completions = _FakeCompletions(stream)


class _FakeClient:
    def __init__(self, stream):
        self.chat = _FakeChat(stream)


class _TailErrorStream:
    def __iter__(self):
        yield {"choices": [{"delta": {"content": "你好"}}]}
        yield {"choices": [{"delta": {"content": "！"}}]}
        raise IndexError("list index out of range")


class TestAIStreamTailHandling(unittest.TestCase):
    def test_prepare_messages_removes_duplicated_current_user_from_history(self):
        ai = ai_module.DeepSeekAI(api_key="test-key")

        messages = ai._prepare_messages(
            "你还会做什么",
            chat_history=[
                {"role": "user", "content": "牛顿环是什么"},
                {"role": "ai", "content": "牛顿环是一种等厚干涉现象。"},
                {"role": "user", "content": "你还会做什么"},
            ],
        )

        conversation = [item for item in messages if item["role"] in {"user", "assistant"}]
        self.assertEqual(
            conversation,
            [
                {"role": "user", "content": "牛顿环是什么"},
                {"role": "assistant", "content": "牛顿环是一种等厚干涉现象。"},
                {"role": "user", "content": "你还会做什么"},
            ],
        )

    def test_chat_stream_ignores_empty_tail_error_after_content(self):
        ai = ai_module.DeepSeekAI(api_key="test-key")
        ai._get_client = lambda: _FakeClient(_TailErrorStream())

        self.assertEqual("".join(ai.chat_stream("你好")), "你好！")

    def test_chat_stream_sends_high_reasoning_effort(self):
        ai = ai_module.DeepSeekAI(api_key="test-key")
        client = _FakeClient(iter([{"choices": [{"delta": {"content": "ok"}}]}]))
        ai._get_client = lambda: client

        self.assertEqual("".join(ai.chat_stream("你好")), "ok")
        self.assertEqual(
            client.chat.completions.last_kwargs["extra_body"]["reasoning_effort"],
            "high",
        )

    def test_streaming_handler_drops_tail_error_text_after_content(self):
        class FakeAI:
            def chat_stream(self, *_args, **_kwargs):
                yield "正文"
                yield f"{ai_module.API_ERROR_PREFIX}list index out of range"

        original_get_ai_instance = ai_module.get_ai_instance
        ai_module.get_ai_instance = lambda: FakeAI()
        try:
            handler = ai_module.StreamingAIHandler("test")
            handler.start_stream("你好")
            handler.current_thread.join(timeout=1)

            self.assertTrue(handler.check_done())
            self.assertEqual(handler.get_full_response(), "正文")
            self.assertEqual(handler.get_next_chunk(), "正文")
            self.assertEqual(handler.get_next_chunk(), "")
        finally:
            ai_module.get_ai_instance = original_get_ai_instance


if __name__ == "__main__":
    unittest.main()
