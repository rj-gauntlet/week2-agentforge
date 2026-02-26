"""
Tests for the eval harness (scripts/run_eval_harness.py).
- Unit test: harness logic with mocked run_agent.
- Optional: full harness run (requires API key, use pytest -m eval).
"""
import json
import os
import sys

import pytest

# Project root
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

# Load harness helpers (same logic as run_eval_harness.py)
from scripts.run_eval_harness import (
    load_eval_cases,
    extract_tools_used,
    run_one_case,
)


def test_load_eval_cases():
    """Eval dataset loads and has expected categories."""
    cases = load_eval_cases()
    assert len(cases) >= 20
    categories = {c.get("category") for c in cases}
    assert "happy_path" in categories
    assert "edge_case" in categories
    for c in cases:
        assert "query" in c
        assert "category" in c


def test_extract_tools_used():
    """Extract tool names from agent messages."""
    class FakeMsg:
        def __init__(self, tool_calls=None):
            self.tool_calls = tool_calls or []

    msgs = [
        FakeMsg(tool_calls=[{"name": "drug_interaction_check"}, {"name": "symptom_lookup"}]),
        FakeMsg(),
    ]
    assert extract_tools_used(msgs) == ["drug_interaction_check", "symptom_lookup"]
    assert extract_tools_used([]) == []


def test_run_one_case_passed():
    """Harness marks case as passed when tools and output match."""
    def mock_run(query):
        return {
            "output": "According to the drug interaction check, these medications may interact.",
            "messages": [type("M", (), {"tool_calls": [{"name": "drug_interaction_check"}]})()],
            "error": None,
        }

    case = {
        "query": "Do aspirin and ibuprofen interact?",
        "category": "happy_path",
        "expected_tools": ["drug_interaction_check"],
        "expected_output_contains": ["interact"],
    }
    r = run_one_case(case, mock_run)
    assert r["passed"] is True
    assert r["tools_ok"] is True
    assert r["output_ok"] is True
    assert r["tools_used"] == ["drug_interaction_check"]


def test_run_one_case_fail_tools():
    """Harness marks failed when expected tool was not used."""
    def mock_run(query):
        return {
            "output": "I don't have that information.",
            "messages": [],
            "error": None,
        }

    case = {
        "query": "Do aspirin and ibuprofen interact?",
        "category": "happy_path",
        "expected_tools": ["drug_interaction_check"],
        "expected_output_contains": ["interact"],
    }
    r = run_one_case(case, mock_run)
    assert r["passed"] is False
    assert r["tools_ok"] is False


def test_run_one_case_fail_output():
    """Harness marks failed when output does not contain expected phrase."""
    def mock_run(query):
        return {
            "output": "I cannot help with that.",
            "messages": [type("M", (), {"tool_calls": [{"name": "drug_interaction_check"}]})()],
            "error": None,
        }

    case = {
        "query": "Do aspirin and ibuprofen interact?",
        "category": "happy_path",
        "expected_tools": ["drug_interaction_check"],
        "expected_output_contains": ["interact"],
    }
    r = run_one_case(case, mock_run)
    assert r["passed"] is False
    assert r["output_ok"] is False


def test_run_one_case_expected_tool_output_passed():
    """Harness passes when structured tool output matches expected_tool_output."""
    class FakeAIMsg:
        tool_calls = [{"id": "call_1", "name": "insurance_coverage_check"}]
    class FakeToolMsg:
        tool_call_id = "call_1"
        content = '{"covered": false, "details": "No coverage found."}'

    def mock_run(query):
        return {
            "output": "Plan does not cover that procedure.",
            "messages": [FakeAIMsg(), FakeToolMsg()],
            "error": None,
        }

    case = {
        "query": "Does plan_001 cover a knee replacement?",
        "category": "multi_step",
        "expected_tools": ["insurance_coverage_check"],
        "expected_output_contains": ["procedure"],
        "expected_tool_output": {"insurance_coverage_check": {"covered": False}},
    }
    r = run_one_case(case, mock_run)
    assert r["passed"] is True
    assert r["tool_output_ok"] is True


def test_run_one_case_expected_tool_output_fail():
    """Harness fails when structured tool output does not match expected_tool_output."""
    class FakeAIMsg:
        tool_calls = [{"id": "call_1", "name": "insurance_coverage_check"}]
    class FakeToolMsg:
        tool_call_id = "call_1"
        content = '{"covered": true, "details": "Covered."}'

    def mock_run(query):
        return {
            "output": "Yes, it is covered.",
            "messages": [FakeAIMsg(), FakeToolMsg()],
            "error": None,
        }

    case = {
        "query": "Does plan_001 cover 99213?",
        "category": "happy_path",
        "expected_tools": ["insurance_coverage_check"],
        "expected_output_contains": ["covered"],
        "expected_tool_output": {"insurance_coverage_check": {"covered": False}},
    }
    r = run_one_case(case, mock_run)
    assert r["passed"] is False
    assert r["tool_output_ok"] is False


@pytest.mark.eval
@pytest.mark.skipif(
    not (os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")),
    reason="API key required for full eval run",
)
def test_full_harness_run():
    """Run full eval harness and assert results are written (optional, slow)."""
    from scripts.run_eval_harness import main

    exit_code = main()
    results_path = os.path.join(ROOT, "data", "eval_results_latest.json")
    assert os.path.isfile(results_path)
    with open(results_path, encoding="utf-8") as f:
        data = json.load(f)
    assert "run_at" in data
    assert "pass_rate_pct" in data
    assert "by_category" in data
    assert "results" in data
    assert len(data["results"]) >= 20
    # Optional: allow non-zero exit if we're not at 100% yet
    # assert exit_code == 0
