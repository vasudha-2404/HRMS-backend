"""Backwards-compatible response utilities (preferred name: responses.py)."""

from app.utils.response import APIResponse, ErrorResponse, error_response, success_response

__all__ = [
    "APIResponse",
    "ErrorResponse",
    "success_response",
    "error_response",
]

