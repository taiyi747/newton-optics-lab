#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Legacy bridge module.

The FastAPI application now calls service-layer functions directly, but this
module is kept as a compatibility wrapper for any older code paths that still
import bridge helpers.
"""

import json

from lib.services.ai_service import (
    ai_chat_stream_chunk,
    ai_chat_stream_start,
    ai_clear_history,
    ai_stop_stream,
)
from lib.services.data_service import process_data
from lib.services.demo_service import (
    calculate_convex_concave_contact,
    calculate_convex_concave_noncontact,
    calculate_convex_convex_contact,
    calculate_convex_convex_noncontact,
    calculate_normal_newton_rings,
    calculate_truncated_newton_rings,
)


API_FUNCTIONS = {
    "demo_normal": calculate_normal_newton_rings,
    "demo_truncated": calculate_truncated_newton_rings,
    "demo_convex_concave_contact": calculate_convex_concave_contact,
    "demo_convex_convex_contact": calculate_convex_convex_contact,
    "demo_convex_concave_noncontact": calculate_convex_concave_noncontact,
    "demo_convex_convex_noncontact": calculate_convex_convex_noncontact,
    "process_data": process_data,
    "ai_chat_stream_start": ai_chat_stream_start,
    "ai_chat_stream_chunk": ai_chat_stream_chunk,
    "ai_stop_stream": ai_stop_stream,
    "ai_clear_history": ai_clear_history,
    "exit": lambda **kwargs: {"success": True, "message": "应用退出"},
}


def call_api(method, params):
    """Compatibility API dispatcher for older bridge-based integrations."""
    if method not in API_FUNCTIONS:
        return json.dumps({"success": False, "error": f"未知方法: {method}"})

    try:
        result = API_FUNCTIONS[method](**params)
    except Exception as exc:
        result = {"success": False, "error": str(exc)}
    return json.dumps(result, ensure_ascii=False)
