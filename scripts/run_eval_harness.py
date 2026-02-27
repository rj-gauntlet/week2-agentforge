"""
Eval harness: automated runner for data/eval_cases.json.
Runs each case through the agent, checks expected_tools, expected_output_contains, expected_flags;
reports pass/fail by category and writes results to data/eval_results_latest.json for regression.

Usage (from project root):
  python scripts/run_eval_harness.py   # or: .venv\\Scripts\\python.exe scripts\\run_eval_harness.py

Optional: set LANGCHAIN_TRACING_V2=true and LANGCHAIN_API_KEY to send traces to LangSmith.
"""
import json
import os
import sys
from datetime import datetime, timezone

# Project root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Load .env before importing orchestrator
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))


def load_eval_cases(filepath=None):
    path = filepath or os.path.join(ROOT, "data", "eval_cases.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def extract_tools_used(messages):
    """From run_agent() result messages, return list of tool names invoked."""
    out = []
    for m in messages or []:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for tc in m.tool_calls:
                name = tc.get("name")
                if name:
                    out.append(name)
    return out


def extract_tool_outputs(messages):
    """
    From run_agent() result messages, return dict: tool_name -> list of parsed output dicts.
    Each tool may be called multiple times; we collect all outputs (LLM sees JSON string from our tools).
    """
    tool_outputs_by_id = {}
    for m in messages or []:
        is_tool_msg = (
            getattr(m, "type", None) == "tool"
            or (getattr(m, "__class__", None) and getattr(m.__class__, "__name__", None) == "ToolMessage")
            or (getattr(m, "tool_call_id", None) is not None and getattr(m, "content", None) is not None)
        )
        if is_tool_msg:
            c = getattr(m, "content", None)
            tid = getattr(m, "tool_call_id", None)
            if tid is not None:
                try:
                    data = json.loads(c) if isinstance(c, str) else c
                    tool_outputs_by_id[tid] = data if isinstance(data, dict) else {}
                except (TypeError, json.JSONDecodeError):
                    tool_outputs_by_id[tid] = {}
    # Map tool_call_id -> tool name from AIMessage tool_calls
    id_to_name = {}
    for m in messages or []:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for tc in m.tool_calls:
                id_to_name[tc.get("id")] = tc.get("name")
    # Build tool_name -> [output1, output2, ...]
    by_name = {}
    for tid, data in tool_outputs_by_id.items():
        name = id_to_name.get(tid)
        if name:
            by_name.setdefault(name, []).append(data)
    return by_name


def run_one_case(case, run_agent_fn):
    """Run a single eval case; return dict with passed, output, tools_used, error, checks."""
    query = case.get("query", "")
    expected_tools = set(case.get("expected_tools") or [])
    expected_contains = case.get("expected_output_contains") or []
    expected_flags = case.get("expected_flags") or {}
    expected_tool_output = case.get("expected_tool_output") or {}

    result = run_agent_fn(query)
    output = (result.get("output") or "").strip()
    err = result.get("error")
    messages = result.get("messages") or []
    tools_used = extract_tools_used(messages)
    tool_outputs = extract_tool_outputs(messages)

    # Check 1: expected tools (all must be present)
    tools_ok = expected_tools.issubset(set(tools_used)) if expected_tools else True

    # Check 2: output contains at least one expected phrase (OR logic)
    output_ok = True
    if expected_contains:
        output_lower = output.lower()
        output_ok = any((k or "").strip().lower() in output_lower for k in expected_contains)

    # Check 3: expected_flags (e.g. can_diagnose: false -> output should not claim diagnosis)
    flags_ok = True
    if expected_flags.get("can_diagnose") is False:
        # Agent must not diagnose; should say consult provider / not a diagnosis
        safe_phrases = ["consult", "not a diagnosis", "cannot diagnose", "can't diagnose", "provider", "not diagnose"]
        output_lower = output.lower()
        flags_ok = any(p in output_lower for p in safe_phrases)

    # Check 4: expected_tool_output (structured tool return values, e.g. insurance_coverage_check.covered)
    tool_output_ok = True
    if expected_tool_output:
        for tool_name, expected_subset in expected_tool_output.items():
            outputs = tool_outputs.get(tool_name, [])
            match = any(
                all(out.get(k) == v for k, v in expected_subset.items())
                for out in outputs
            )
            if not match:
                tool_output_ok = False
                break

    passed = tools_ok and output_ok and flags_ok and tool_output_ok and not err
    return {
        "query": query,
        "category": case.get("category", "unknown"),
        "passed": passed,
        "tools_ok": tools_ok,
        "output_ok": output_ok,
        "flags_ok": flags_ok,
        "tool_output_ok": tool_output_ok,
        "no_error": not bool(err),
        "tools_used": tools_used,
        "expected_tools": list(expected_tools),
        "error": err,
        "output_preview": (output[:300] + "…") if len(output) > 300 else output,
    }


def main():
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env to run the eval harness.")
        sys.exit(1)

    from agent.orchestrator import run_agent
    import time

    cases = load_eval_cases()
    print(f"Running eval harness on {len(cases)} cases from data/eval_cases.json ...")
    results = []
    for i, case in enumerate(cases):
        r = run_one_case(case, lambda q: run_agent(q, source="eval"))
        results.append(r)
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  [{i+1}/{len(cases)}] {status}  {r['category']}: {r['query'][:50]}…")
        # Sleep briefly to avoid hitting OpenAI rate limits
        time.sleep(1.5)

    # Aggregate by category
    by_cat = {}
    for r in results:
        c = r["category"]
        if c not in by_cat:
            by_cat[c] = {"total": 0, "passed": 0}
        by_cat[c]["total"] += 1
        if r["passed"]:
            by_cat[c]["passed"] += 1

    total = len(results)
    passed_total = sum(1 for r in results if r["passed"])
    overall_rate = (passed_total / total * 100) if total else 0

    print("\n--- By category ---")
    for cat, stats in sorted(by_cat.items()):
        pct = (stats["passed"] / stats["total"] * 100) if stats["total"] else 0
        print(f"  {cat}: {stats['passed']}/{stats['total']} ({pct:.0f}%)")
    print(f"\n--- Overall: {passed_total}/{total} ({overall_rate:.1f}%) ---")

    # Save results for regression / observability
    run_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    payload = {
        "run_at": run_at,
        "total": total,
        "passed": passed_total,
        "pass_rate_pct": round(overall_rate, 1),
        "by_category": {c: {"total": s["total"], "passed": s["passed"], "pass_rate_pct": round((s["passed"] / s["total"] * 100) if s["total"] else 0, 1)} for c, s in by_cat.items()},
        "results": results,
    }
    out_dir = os.path.join(ROOT, "data", "eval_results")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(ROOT, "data", "eval_results_latest.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    # Historical copy for regression tracking (timestamped, not overwritten)
    stamp = run_at.replace(":", "-").replace(".", "-")[:19]
    history_path = os.path.join(out_dir, f"eval_{stamp}Z.json")
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"\nResults written to {out_path}")
    print(f"History copy: {history_path}")

    return 0 if passed_total == total else 1


if __name__ == "__main__":
    sys.exit(main())
