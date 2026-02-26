# Evaluation (Eval) Framework

This document describes the eval dataset format and how to run evaluations for submission and open-source use.

---

## Quick start

From the project root (with `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in `.env`):

```powershell
.\.venv\Scripts\python.exe scripts\run_eval_harness.py
```

- **Output:** Pass/fail per case and per-category summary in the terminal.
- **Latest run:** `data/eval_results_latest.json` (overwritten each run).
- **History:** Each run is also saved under `data/eval_results/eval_<timestamp>Z.json` for regression tracking.

---

## Dataset format (`data/eval_cases.json`)

Each case is a JSON object with:

| Field | Required | Description |
|-------|----------|-------------|
| `category` | Yes | One of: `happy_path`, `edge_case`, `adversarial`, `multi_step`. |
| `query` | Yes | The user prompt sent to the agent. |
| `expected_tools` | Yes* | List of tool names that must be invoked (e.g. `["drug_interaction_check"]`). Use `[]` when no tool should be called. |
| `expected_output_contains` | Yes* | List of phrases; **at least one** must appear in the agent’s final reply (OR logic). |
| `expected_flags` | No | E.g. `{"can_diagnose": false}` — requires a consult-provider / no-diagnosis disclaimer in the output. |
| `expected_tool_output` | No | Structured check on tool return values. Example: `{"insurance_coverage_check": {"covered": false}}` — at least one call to that tool must return JSON containing those key-value pairs. Use this to assert on structured data instead of wording. |

\*For evals that only care about tool output, `expected_output_contains` can be a minimal list (e.g. one keyword); `expected_tool_output` carries the main assertion.

---

## How the harness works

1. Loads `data/eval_cases.json`.
2. For each case: runs the agent with `query`, then checks:
   - **Tools:** All `expected_tools` were used.
   - **Output:** The final reply contains at least one of `expected_output_contains`.
   - **Flags:** If `expected_flags.can_diagnose === false`, the reply must include a safe disclaimer.
   - **Tool output:** If `expected_tool_output` is set, the parsed return value(s) of the named tool(s) must match the given key-value pairs.
3. Writes `eval_results_latest.json` and a timestamped copy under `data/eval_results/`.
4. Exit code `0` if all cases pass, `1` otherwise.

---

## Observability

- Set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` in `.env` to send traces to LangSmith for each run.
- Historical runs in `data/eval_results/` give a simple regression view; combine with LangSmith for deeper analysis.

---

## Pytest

Run harness-related unit tests (no API key needed):

```powershell
.\.venv\Scripts\python.exe -m pytest tests/eval/test_eval_harness.py -v -m "not eval"
```

Run the full harness via pytest (requires API key):

```powershell
.\.venv\Scripts\python.exe -m pytest tests/eval/test_eval_harness.py -v -m eval
```

---

## Deferred follow-up

See **`data/EVAL_TODO.md`** for a short note on two failing cases to revisit later (edge_case “When is prov_999 available?” and adversarial “hack a hospital database”).
