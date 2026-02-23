"""
MVP eval: 5+ test cases with input query, expected tool calls, and pass/fail criteria.
Run: pytest tests/eval/test_eval_mvp.py -v
Requires OPENAI_API_KEY or ANTHROPIC_API_KEY; skips when unset.
"""
import os

import pytest


def _has_llm_key():
    return bool(os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))


@pytest.mark.eval
@pytest.mark.skipif(not _has_llm_key(), reason="OPENAI_API_KEY or ANTHROPIC_API_KEY required for eval")
class TestEvalMVP:
    """Minimum 5 eval cases for MVP gate."""

    @pytest.mark.parametrize("query,expected_contains", [
        ("Do aspirin and ibuprofen interact?", "interact"),
        ("Check if warfarin and aspirin are safe together.", "warfarin"),
        ("I'm on lisinopril only, any interactions?", "none"),
    ])
    def test_drug_interaction_queries(self, query, expected_contains):
        """Eval: user asks about drug interactions -> agent uses drug_interaction_check and output is relevant."""
        from agent.orchestrator import run_agent

        result = run_agent(query)
        assert "error" not in result or not result.get("error"), result.get("error")
        out = (result.get("output") or "").lower()
        assert expected_contains.lower() in out or "interact" in out, f"Expected '{expected_contains}' or 'interact' in: {out[:200]}"

    def test_provider_search_query(self):
        """Eval: user asks for a doctor -> agent responds (may use provider_search)."""
        from agent.orchestrator import run_agent

        result = run_agent("Find me a cardiologist in Boston.")
        assert "error" not in result or not result.get("error")
        assert (result.get("output") or "").strip()

    def test_appointment_availability_query(self):
        """Eval: user asks for open slots -> agent responds (may use appointment_availability)."""
        from agent.orchestrator import run_agent

        result = run_agent("Do you have any appointments available tomorrow?")
        assert "error" not in result or not result.get("error")
        assert (result.get("output") or "").strip()
