# -*- coding: utf-8 -*-
"""
AI 助手 API - SSE 流式对话接口
"""

import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

from lib.ai_module import (
    API_ERROR_PREFIX,
    REQUEST_TIMEOUT_SECONDS,
    create_stream,
    remove_stream,
)

router = APIRouter()
SSE_HEARTBEAT_SECONDS = 10
SSE_IDLE_TIMEOUT_SECONDS = REQUEST_TIMEOUT_SECONDS + 10


def _sse_data(payload) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _sse_comment(comment: str) -> str:
    return f": {comment}\n\n"


def _openai_content_chunk(content: str) -> dict:
    return {
        "choices": [
            {
                "index": 0,
                "delta": {"content": content},
                "finish_reason": None,
            }
        ]
    }


def _openai_error_chunk(message: str) -> dict:
    return {
        "choices": [
            {
                "index": 0,
                "delta": {"content": f"{API_ERROR_PREFIX}{message}"},
                "finish_reason": "error",
            }
        ]
    }


# ==================== 请求模型 ====================

class AttachmentItem(BaseModel):
    name: str
    type: str
    size: int = 0
    data: str  # base64

class AiChatParams(BaseModel):
    message: str
    attachments: Optional[List[AttachmentItem]] = None
    chat_history: Optional[List[dict]] = None
    context_prompt: Optional[str] = None


# ==================== SSE 流式对话 ====================

@router.post("/ai_chat")
async def ai_chat(params: AiChatParams):
    """
    AI 流式对话 - SSE 推送

    前端用 fetch + ReadableStream 读取，后端持续推送 OpenAI 风格 SSE：
        data: {"choices":[{"delta":{"content":"文本片段"}}]}\n\n
        data: {"choices":[{"delta":{"content":"更多文本"}}]}\n\n
        data: [DONE]\n\n
    """
    import asyncio
    import time

    async def event_generator():
        stream_id = f"sse_{id(params)}_{__import__('time').time()}"
        handler = create_stream(stream_id)
        sent_content = False
        last_activity_at = time.monotonic()
        last_heartbeat_at = last_activity_at

        attachments = None
        if params.attachments:
            attachments = [a.model_dump() for a in params.attachments]

        chat_history = params.chat_history if params.chat_history else None

        # 在后台线程启动流式响应
        handler.start_stream(
            params.message or "(已上传附件)",
            attachments=attachments,
            chat_history=chat_history,
            context_prompt=params.context_prompt
        )

        try:
            while True:
                chunk = handler.get_next_chunk()
                if chunk:
                    sent_content = True
                    last_activity_at = time.monotonic()
                    last_heartbeat_at = last_activity_at
                    yield _sse_data(_openai_content_chunk(chunk))
                elif handler.check_done():
                    if handler.last_error and not sent_content:
                        yield _sse_data(_openai_error_chunk(handler.last_error))
                    yield "data: [DONE]\n\n"
                    break
                else:
                    now = time.monotonic()
                    if now - last_activity_at > SSE_IDLE_TIMEOUT_SECONDS:
                        handler.stop()
                        message = f"上游模型响应超时（超过 {SSE_IDLE_TIMEOUT_SECONDS} 秒未返回内容）"
                        if sent_content:
                            yield _sse_data(_openai_content_chunk(f"\n\n{message}"))
                        else:
                            yield _sse_data(_openai_error_chunk(message))
                        yield "data: [DONE]\n\n"
                        break

                    if now - last_heartbeat_at >= SSE_HEARTBEAT_SECONDS:
                        last_heartbeat_at = now
                        yield _sse_comment("ping")

                    await asyncio.sleep(0.05)
        finally:
            remove_stream(stream_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# ==================== 停止生成 ====================

@router.post("/ai_stop")
async def ai_stop():
    """停止 AI 当前生成（如果有的话）"""
    return {"success": True}
