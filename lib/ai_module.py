#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI assistant module backed by an OpenAI-compatible chat API.

This module keeps the public API used by the existing frontend/service layer:
`DeepSeekAI`, `ai_chat`, `ai_chat_stream`, `StreamingAIHandler`, and stream
registry helpers.
"""

import base64
import logging
import os
import threading
from collections import deque
from typing import Callable, Deque, Dict, Generator, List, Optional

logger = logging.getLogger(__name__)

# 配置加载顺序：环境变量 > .env 文件 > _config_built.py（构建时生成）> 默认值
# 开源发布时请勿在 _config_built.py 中放置真实 API key
_CONFIG_DEFAULTS = {
    "AI_API_KEY": "",
    "AI_API_BASE_URL": "https://api.siliconflow.cn",
    "AI_MODEL": "deepseek-ai/DeepSeek-V4-Flash",
    "AI_REASONING_EFFORT": "high",
}

_BUILT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "_config_built.py")


def _load_config(key: str) -> str:
    """从多级配置源加载配置。"""
    # 1. 环境变量（最高优先级）
    value = os.getenv(key)
    if value:
        return value

    # 2. .env 文件（项目根目录）
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith(key + "="):
                    value = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if value:
                        return value

    # 3. 构建时生成的配置
    if os.path.exists(_BUILT_CONFIG_PATH):
        import importlib.util

        spec = importlib.util.spec_from_file_location("_config_built", _BUILT_CONFIG_PATH)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, key):
                value = getattr(module, key)
                if value:
                    return value

    # 4. 默认值
    return _CONFIG_DEFAULTS.get(key, "")


API_KEY = _load_config("AI_API_KEY")
API_KEY_PLACEHOLDER = "<请在 .env 中设置 AI_API_KEY>"
API_BASE_URL = _load_config("AI_API_BASE_URL")
MODEL = _load_config("AI_MODEL")
REASONING_EFFORT = _load_config("AI_REASONING_EFFORT")
REQUEST_TIMEOUT_SECONDS = 35

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OpenAI = None
    OPENAI_AVAILABLE = False
    logger.warning("未安装 OpenAI SDK，请运行: pip install openai")


SYSTEM_PROMPT = r"""你是一个专业、严谨、易懂的 AI 学习助手。

回答规则：
- 使用中文回答，表达准确、清晰，适合大学生学习和实验场景。
- 如果问题复杂，可以分步骤解释，并使用自然段落和序号（1. 2. 3.）组织内容。
- 不要使用 Markdown 代码块包裹普通回答或公式。
- 涉及公式、推导、变量关系时，优先使用 KaTeX/LaTeX 兼容语法，便于前端渲染。
- 行内公式使用单美元符号，例如：$t=\frac{r^2}{2R}$。
- 独立展示的重要公式使用双美元符号，例如：$$r_m^2=m\lambda R$$。
- 如果前端提供了额外实验上下文，请优先结合该上下文回答。
"""

MISSING_KEY_MESSAGE = "错误：未配置 API 密钥。请在 lib/ai_module.py 顶部设置 API_KEY"
MISSING_SDK_MESSAGE = "错误：未安装 OpenAI SDK。请运行: pip install openai"
MAX_ATTACHMENT_CHARS = 8000
MAX_HISTORY_MESSAGES = 12
MAX_HISTORY_CHARS = 12000
API_ERROR_PREFIX = "错误：API请求失败 - "
EMPTY_TAIL_ERROR_MARKERS = ("list index out of range",)


def _get_field(value, name: str, default=None):
    """Read either object attributes or dict keys from SDK/provider objects."""
    if isinstance(value, dict):
        return value.get(name, default)
    return getattr(value, name, default)


def _extract_stream_content(chunk) -> str:
    """Extract text from a stream chunk and tolerate provider-specific tail chunks."""
    choices = _get_field(chunk, "choices")
    if not choices:
        return ""

    try:
        choice = choices[0]
    except (IndexError, TypeError, KeyError):
        return ""

    delta = _get_field(choice, "delta")
    message = _get_field(choice, "message")
    content = _get_field(delta, "content") if delta else None
    if content is None and message:
        content = _get_field(message, "content")

    return content or ""


def _extract_message_content(response) -> str:
    choices = _get_field(response, "choices")
    if not choices:
        return ""

    try:
        message = _get_field(choices[0], "message")
    except (IndexError, TypeError, KeyError):
        return ""

    return _get_field(message, "content", "") or ""


def _is_empty_tail_error(exc: Exception) -> bool:
    """OpenAI-compatible providers sometimes fail while parsing the final empty chunk."""
    text = str(exc).lower()
    return isinstance(exc, IndexError) or any(marker in text for marker in EMPTY_TAIL_ERROR_MARKERS)


def _is_empty_tail_error_text(text: str) -> bool:
    """Detect an API error chunk that is only a malformed stream tail."""
    if not text or not text.startswith(API_ERROR_PREFIX):
        return False
    lowered = text.lower()
    return any(marker in lowered for marker in EMPTY_TAIL_ERROR_MARKERS)


def _decode_attachment_data(data: str) -> Optional[str]:
    if not data:
        return None

    # Frontends sometimes send a data URL; keep only the base64 payload.
    if "," in data and data.lstrip().startswith("data:"):
        data = data.split(",", 1)[1]

    try:
        return base64.b64decode(data).decode("utf-8", errors="replace")
    except Exception:
        return None


def _compact_chat_history(chat_history: Optional[list], current_user_content: str) -> List[dict]:
    """Normalize frontend history and remove the current message if duplicated."""
    if not chat_history:
        return []

    normalized: List[dict] = []
    for item in chat_history:
        if not isinstance(item, dict):
            continue

        role = item.get("role")
        if role == "ai":
            role = "assistant"

        content = item.get("content")
        if role not in {"user", "assistant"} or not content:
            continue

        text = str(content).strip()
        if not text:
            continue

        if normalized and normalized[-1]["role"] == role:
            normalized[-1]["content"] = f"{normalized[-1]['content']}\n\n{text}"
        else:
            normalized.append({"role": role, "content": text})

    if normalized and normalized[-1]["role"] == "user":
        if normalized[-1]["content"].strip() == current_user_content.strip():
            normalized.pop()

    selected: List[dict] = []
    total_chars = 0
    for item in reversed(normalized[-MAX_HISTORY_MESSAGES:]):
        content_len = len(item["content"])
        if selected and total_chars + content_len > MAX_HISTORY_CHARS:
            break
        selected.append(item)
        total_chars += content_len

    return list(reversed(selected))


class DeepSeekAI:
    """Small OpenAI-compatible chat client wrapper."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or API_KEY
        self.base_url = base_url or API_BASE_URL
        self.model = model or MODEL
        self._client = None

    def _get_client(self):
        if not OPENAI_AVAILABLE:
            raise ImportError(MISSING_SDK_MESSAGE)

        # Create a fresh client for each chat request. Some OpenAI-compatible
        # streaming gateways can leave a pooled connection in a bad state after
        # a completed stream, which then makes the next turn appear to hang.
        return OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

    def set_api_key(self, api_key: str) -> None:
        self.api_key = api_key
        self._client = None

    def _prepare_messages(
        self,
        user_message: str,
        attachments: Optional[list] = None,
        chat_history: Optional[list] = None,
        context_prompt: Optional[str] = None,
    ) -> List[dict]:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if context_prompt:
            messages.append({"role": "system", "content": str(context_prompt)})

        user_content = self._build_user_content(user_message, attachments)

        for item in _compact_chat_history(chat_history, user_content):
            messages.append(item)

        messages.append({"role": "user", "content": user_content})
        return messages

    def _build_user_content(self, user_message: str, attachments: Optional[list] = None) -> str:
        text_parts = [user_message] if user_message else []

        for attachment in attachments or []:
            if not isinstance(attachment, dict):
                continue

            name = attachment.get("name") or "附件"
            mime_type = attachment.get("type") or "application/octet-stream"
            data = attachment.get("data") or ""

            if mime_type.startswith("image/"):
                text_parts.append(f"[用户上传了图片：{name}。当前模型按文本模式处理，无法直接读取图片内容。]")
                continue

            decoded = _decode_attachment_data(data)
            if decoded:
                if len(decoded) > MAX_ATTACHMENT_CHARS:
                    decoded = decoded[:MAX_ATTACHMENT_CHARS] + "\n...（文件过长，已截断）"
                text_parts.append(f"[附件：{name}]\n{decoded}")
            else:
                text_parts.append(f"[附件：{name}（无法解析文件内容）]")

        return "\n\n".join(text_parts) if text_parts else ""

    def _ensure_ready(self) -> Optional[str]:
        if not self.api_key or not str(self.api_key).strip():
            logger.error("未配置 API 密钥")
            return MISSING_KEY_MESSAGE
        if not OPENAI_AVAILABLE:
            logger.error("未安装 OpenAI SDK")
            return MISSING_SDK_MESSAGE
        return None

    def chat_stream(
        self,
        message: str,
        attachments: Optional[list] = None,
        chat_history: Optional[list] = None,
        context_prompt: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """Stream chat text. Errors after partial output are logged, not appended."""
        readiness_error = self._ensure_ready()
        if readiness_error:
            yield readiness_error
            return

        received_content = False
        client = None
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=self._prepare_messages(
                    message,
                    attachments=attachments,
                    chat_history=chat_history,
                    context_prompt=context_prompt,
                ),
                stream=True,
                extra_body={"reasoning_effort": REASONING_EFFORT},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )

            for chunk in response:
                content = _extract_stream_content(chunk)
                if content:
                    received_content = True
                    yield content

        except Exception as exc:
            if received_content:
                if _is_empty_tail_error(exc):
                    logger.debug("忽略流式响应尾部空 chunk 解析异常: %s", exc)
                else:
                    logger.error("流式响应已输出部分内容后中断: %s", exc)
                return

            logger.error("API 请求失败: %s", exc)
            yield f"{API_ERROR_PREFIX}{exc}"
        finally:
            close_client = getattr(client, "close", None)
            if callable(close_client):
                close_client()

    def chat(self, message: str, chat_history: Optional[list] = None) -> str:
        readiness_error = self._ensure_ready()
        if readiness_error:
            return readiness_error

        client = None
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=self._prepare_messages(message, chat_history=chat_history),
                stream=False,
                extra_body={"reasoning_effort": REASONING_EFFORT},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            content = _extract_message_content(response)
            return content or "错误：API返回空内容"
        except Exception as exc:
            logger.error("API 请求失败: %s", exc)
            return f"{API_ERROR_PREFIX}{exc}"
        finally:
            close_client = getattr(client, "close", None)
            if callable(close_client):
                close_client()


def _new_client(api_key: str):
    if not OPENAI_AVAILABLE:
        raise ImportError(MISSING_SDK_MESSAGE)
    return OpenAI(api_key=api_key, base_url=API_BASE_URL, timeout=REQUEST_TIMEOUT_SECONDS)


def test_connection() -> bool:
    """Test a non-streaming request against the configured API."""
    if not OPENAI_AVAILABLE:
        logger.error("OpenAI SDK not installed")
        return False

    if not API_KEY or not str(API_KEY).strip():
        logger.error("API_KEY not set")
        return False

    try:
        response = _new_client(API_KEY).chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"},
            ],
            stream=False,
            extra_body={"reasoning_effort": REASONING_EFFORT},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        ok = bool(_extract_message_content(response))
        logger.info("API connection test %s", "successful" if ok else "returned empty content")
        return ok
    except Exception as exc:
        logger.error("API connection test failed: %s", exc)
        return False


def test_streaming() -> bool:
    """Test a streaming request against the configured API."""
    if not OPENAI_AVAILABLE:
        logger.error("OpenAI SDK not installed")
        return False

    if not API_KEY or not str(API_KEY).strip():
        logger.error("API_KEY not set")
        return False

    try:
        response = _new_client(API_KEY).chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "请用一句话介绍牛顿环实验"},
            ],
            stream=True,
            extra_body={"reasoning_effort": REASONING_EFFORT},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        print("Streaming response: ", end="", flush=True)
        full_content = []
        try:
            for chunk in response:
                content = _extract_stream_content(chunk)
                if content:
                    print(content, end="", flush=True)
                    full_content.append(content)
        except Exception as exc:
            if full_content and _is_empty_tail_error(exc):
                logger.debug("忽略流式响应尾部空 chunk 解析异常: %s", exc)
            else:
                raise

        print("\n\nStreaming test completed!")
        return bool(full_content)
    except Exception as exc:
        logger.error("Streaming test failed: %s", exc)
        return False


_ai_instance: Optional[DeepSeekAI] = None
_streaming_handler = None
active_streams: Dict[str, "StreamingAIHandler"] = {}


def get_ai_instance() -> DeepSeekAI:
    global _ai_instance
    if _ai_instance is None:
        _ai_instance = DeepSeekAI()
    return _ai_instance


def reset_ai_instance() -> None:
    global _ai_instance
    _ai_instance = None


def clear_ai_history() -> None:
    """Clear transient AI state kept in memory by the backend."""
    reset_ai_instance()

    for handler in list(active_streams.values()):
        handler.stop()
    active_streams.clear()

    global _streaming_handler
    if _streaming_handler:
        _streaming_handler.stop()
    _streaming_handler = None


def ai_chat(message: str) -> str:
    return get_ai_instance().chat(message)


def ai_chat_stream(message: str, chat_history: Optional[list] = None) -> Generator[str, None, None]:
    yield from get_ai_instance().chat_stream(message, chat_history=chat_history)


def set_ai_api_key(api_key: str) -> None:
    get_ai_instance().set_api_key(api_key)


class StreamingAIHandler:
    """Background-thread wrapper for polling streamed AI chunks."""

    def __init__(self, stream_id: Optional[str] = None):
        self.stream_id = stream_id
        self.is_running = False
        self._is_done = False
        self.current_thread: Optional[threading.Thread] = None
        self.response_buffer: List[str] = []
        self.chunk_queue: Deque[str] = deque()
        self.last_error: Optional[str] = None
        self.lock = threading.Lock()

    def start_stream(
        self,
        message: str,
        on_chunk: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[], None]] = None,
        attachments: Optional[list] = None,
        chat_history: Optional[list] = None,
        context_prompt: Optional[str] = None,
    ) -> None:
        if self.is_running:
            logger.debug("Stream %s already running", self.stream_id)
            return

        with self.lock:
            self.is_running = True
            self._is_done = False
            self.response_buffer = []
            self.chunk_queue = deque()
            self.last_error = None

        def stream_worker() -> None:
            try:
                stream = get_ai_instance().chat_stream(
                    message,
                    attachments=attachments,
                    chat_history=chat_history,
                    context_prompt=context_prompt,
                )
                for chunk in stream:
                    if not self.is_running:
                        break
                    with self.lock:
                        if _is_empty_tail_error_text(chunk) and self.response_buffer:
                            logger.debug("忽略已输出正文后的流式尾部错误片段: %s", chunk)
                            continue
                        self.response_buffer.append(chunk)
                        self.chunk_queue.append(chunk)
                    if on_chunk:
                        on_chunk(chunk)
            except Exception as exc:
                logger.error("Stream worker error: %s", exc)
                with self.lock:
                    self.last_error = str(exc)
            finally:
                with self.lock:
                    self.is_running = False
                    self._is_done = True
                if on_complete:
                    on_complete()

        self.current_thread = threading.Thread(target=stream_worker, daemon=True)
        self.current_thread.start()
        logger.debug("Stream %s started", self.stream_id)

    def stop(self) -> None:
        with self.lock:
            self.is_running = False
        logger.debug("Stream %s stopped", self.stream_id)

    def get_next_chunk(self) -> str:
        with self.lock:
            if self.chunk_queue:
                return self.chunk_queue.popleft()
            return ""

    def check_done(self) -> bool:
        with self.lock:
            return self._is_done

    def get_full_response(self) -> str:
        with self.lock:
            return "".join(self.response_buffer)


def create_stream(stream_id: str) -> StreamingAIHandler:
    handler = StreamingAIHandler(stream_id)
    active_streams[stream_id] = handler
    return handler


def get_streaming_handler(stream_id: Optional[str] = None) -> StreamingAIHandler:
    if stream_id:
        return active_streams.get(stream_id) or create_stream(stream_id)

    global _streaming_handler
    if _streaming_handler is None:
        _streaming_handler = StreamingAIHandler()
    return _streaming_handler


def remove_stream(stream_id: str) -> None:
    handler = active_streams.pop(stream_id, None)
    if handler:
        handler.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 50)
    print("DeepSeek AI 模块测试")
    print("=" * 50)

    print("\n1. 测试非流式 API 连接...")
    if test_connection():
        print("\n2. 测试流式 API...")
        test_streaming()

        print("\n3. 测试 AI 助手类...")
        ai = DeepSeekAI()
        print("\n提问: 牛顿环是什么？")
        print("回答: ", end="", flush=True)
        for text in ai.chat_stream("牛顿环是什么？"):
            print(text, end="", flush=True)
        print("\n")
    else:
        print("\nAPI 连接测试失败，请检查：")
        print("1. 是否已安装 OpenAI SDK: pip install openai")
        print("2. 是否已在 lib/ai_module.py 顶部设置 API_KEY")
        print("3. 网络连接是否正常")
