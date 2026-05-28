"""Standardized API response utilities."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Success"
    data: T | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str


def success_response(
    data: Any = None,
    message: str = "Success",
) -> dict[str, Any]:
    return {"success": True, "message": message, "data": data}


def error_response(error: str) -> dict[str, Any]:
    return {"success": False, "error": error}
