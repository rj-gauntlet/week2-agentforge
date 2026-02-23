# Testing & TDD Guide

This project uses **test-driven development (TDD)** for the MVP. Tests define the contract; we implement until they pass.

---

## Quick start

```bash
# 1. From project root, create a venv (recommended) and install dependencies
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# Copy env (add your LLM API key when you need the agent)
cp .env.example .env

# Run all tests (unit + integration + eval)
pytest

# Run only unit tests (fast; no LLM calls)
pytest tests/unit -v

# Run only eval cases (once agent exists)
pytest tests/eval -v -m eval
```

---

## Environment for eval and integration tests

Eval and integration tests call the real agent (and thus the LLM). They need **`OPENAI_API_KEY`** or **`ANTHROPIC_API_KEY`** to be set. Easiest approach:

1. Copy `.env.example` to `.env` and add your key, e.g. `OPENAI_API_KEY=sk-...`
2. **`tests/conftest.py` loads `.env` from the project root automatically** when pytest starts, so the key is visible to skip conditions and to the orchestrator. You don’t need to `source .env` or set the variable in the shell.
3. If the key is not set, eval and integration tests are **skipped** (not failed).

Unit tests do not need any API key.

---

## Test layout

| Directory | Purpose | When to run |
|-----------|---------|-------------|
| `tests/unit/` | One tool in isolation (mock inputs, assert output shape) | Every change to a tool |
| `tests/integration/` | Agent + tools end-to-end (real or mocked LLM) | After orchestrator exists |
| `tests/eval/` | Eval cases: query → expected tool + output (MVP: 5+; final: 50+) | Before deploy; for regression |

---

## TDD loop (red → green → refactor)

1. **Red:** Write a failing test (or run existing ones: `pytest tests/unit -v`). You should see failures.
2. **Green:** Implement the minimum code (e.g. `agent/tools/drug_interaction_check.py`) so the test passes.
3. **Refactor:** Clean up without changing behavior; tests stay green.

**First cycle:** The hero tool `drug_interaction_check` has unit tests in `tests/unit/test_drug_interaction_check.py`. The implementation in `agent/tools/drug_interaction_check.py` is a stub. Implement loading a curated dataset (e.g. `data/drug_interactions.json`) and look up pairs so all tests pass.

---

## What you need to do to succeed

1. **Run tests from the project root:**  
   `cd c:\Users\rjxxl\projects\week2-agentforge` then `pytest tests/unit -v`.

2. **Implement one tool at a time:**  
   Start with `drug_interaction_check`: add a small JSON/CSV of known interactions (e.g. aspirin+ibuprofen → minor, warfarin+aspirin → major), load it in the tool, and return the right shape so unit tests pass.

3. **Keep the contract:**  
   Every tool must return `{ "success": bool, "data": ...?, "error": ...? }`. Use `agent/tools/schemas.py` `tool_result()`.

4. **Add agent tests when ready:**  
   Once you have an orchestrator (LangChain agent + tools), add integration tests that send a query and assert the right tool was called and the response is coherent. Eval cases in `tests/eval/test_eval_mvp.py` can then call the agent instead of skipping.

5. **Eval cases = your 5+ MVP tests:**  
   Each row in `test_eval_mvp.py` (or a data file you load) is one test case: input query, expected tool(s), and a condition on the output. Running `pytest tests/eval` is your “simple evaluation” for the MVP gate.

---

## Commands reference

```bash
pytest                    # all tests
pytest tests/unit -v      # unit only
pytest -m unit            # by marker
pytest -m "not eval"      # skip eval (e.g. while building)
pytest --tb=long         # full tracebacks
```
