"""
Cost tracking for AI Cost Analysis.
Logs token usage and estimated cost per agent run to data/cost_log.jsonl.
Used for dev/test spend and to feed production cost projections.
"""
import json
import os
from datetime import datetime, timezone
from typing import Any

# Approximate USD per 1M tokens (as of 2024; update for current pricing)
PRICING = {
    "openai:gpt-4o": {"input": 2.50, "output": 10.00},
    "anthropic:claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "default": {"input": 3.00, "output": 12.00},
}


def _get_data_dir() -> str:
    """Project data directory (same as eval_cases.json)."""
    return os.path.join(os.path.dirname(__file__), "..", "data")


def _estimate_usd(input_tokens: int, output_tokens: int, model_hint: str | None) -> float:
    """Estimate cost in USD from token counts. model_hint e.g. 'openai:gpt-4o' or 'anthropic:...'."""
    rates = PRICING.get(model_hint or "", PRICING["default"])
    return (input_tokens / 1_000_000 * rates["input"]) + (output_tokens / 1_000_000 * rates["output"])


def extract_usage_from_messages(messages: list[Any], model_hint: str | None = None) -> dict[str, Any]:
    """
    Sum token usage from all AIMessages that have usage_metadata (or response_metadata.usage).
    Returns dict: input_tokens, output_tokens, total_tokens, estimated_usd, model_hint.
    """
    total_in = 0
    total_out = 0
    for m in messages or []:
        if getattr(m, "__class__", None) and "AI" in getattr(m.__class__, "__name__", ""):
            use_meta = getattr(m, "usage_metadata", None)
            resp_meta = getattr(m, "response_metadata", None) or {}
            if isinstance(use_meta, dict):
                total_in += int(use_meta.get("input_tokens") or 0)
                total_out += int(use_meta.get("output_tokens") or 0)
            elif isinstance(resp_meta, dict) and "usage" in resp_meta and isinstance(resp_meta["usage"], dict):
                u = resp_meta["usage"]
                total_in += int(u.get("prompt_tokens") or u.get("input_tokens") or 0)
                total_out += int(u.get("completion_tokens") or u.get("output_tokens") or 0)
    total = total_in + total_out
    estimated_usd = _estimate_usd(total_in, total_out, model_hint) if total else 0.0
    return {
        "input_tokens": total_in,
        "output_tokens": total_out,
        "total_tokens": total,
        "estimated_usd": round(estimated_usd, 6),
        "model_hint": model_hint,
    }


def get_model_hint() -> str:
    """Infer which model is in use from env for cost lookup."""
    if os.getenv("OPENAI_API_KEY"):
        return "openai:gpt-4o"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic:claude-sonnet-4-20250514"
    return "default"


def log_run(
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
    estimated_usd: float,
    model_hint: str | None = None,
    query_preview: str | None = None,
    source: str = "api",
) -> None:
    """
    Append one run to data/cost_log.jsonl.
    source: 'api' | 'eval' | 'script' for filtering later.
    """
    data_dir = _get_data_dir()
    os.makedirs(data_dir, exist_ok=True)
    log_path = os.path.join(data_dir, "cost_log.jsonl")
    preview = (query_preview or "")[:120].replace("\n", " ")
    entry = {
        "ts": datetime.now(tz=timezone.utc).isoformat(),
        "source": source,
        "model_hint": model_hint or get_model_hint(),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "estimated_usd": round(estimated_usd, 6),
        "query_preview": preview,
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
