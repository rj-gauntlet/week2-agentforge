"""Shared response shape for all tools (PRE_SEARCH: { success, data?, error? })."""
from typing import Any, Optional


def tool_result(success: bool, data: Optional[Any] = None, error: Optional[str] = None) -> dict:
    """Return a standard tool result dict."""
    out: dict = {"success": success}
    if data is not None:
        out["data"] = data
    if error is not None:
        out["error"] = error
    return out
