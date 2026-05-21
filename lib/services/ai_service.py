# -*- coding: utf-8 -*-
"""AI streaming service wrappers."""

from lib.ai_module import clear_ai_history, create_stream, get_streaming_handler, remove_stream


def ai_chat_stream_start(message, stream_id):
    try:
        handler = create_stream(stream_id)
        handler.start_stream(message)
        return {"success": True}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def ai_chat_stream_chunk(stream_id):
    try:
        handler = get_streaming_handler(stream_id)
        return {
            "success": True,
            "chunk": handler.get_next_chunk(),
            "done": handler.check_done(),
        }
    except Exception as exc:
        return {"success": False, "error": str(exc), "chunk": "", "done": True}


def ai_stop_stream(stream_id):
    try:
        handler = get_streaming_handler(stream_id)
        handler.stop()
        remove_stream(stream_id)
        return {"success": True}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def ai_clear_history():
    try:
        clear_ai_history()
        return {"success": True}
    except Exception as exc:
        return {"success": False, "error": str(exc)}
