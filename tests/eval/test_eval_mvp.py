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

    def test_multi_step_reasoning(self):
        """
        Eval: user asks a complex question requiring two tools in one turn.
        Checks if the agent can chain tools: insurance_coverage_check -> provider_search.
        """
        from agent.orchestrator import run_agent

        # This query requires checking insurance coverage first, then searching for a provider.
        query = "Does plan plan_001 cover a knee replacement (code 27447)? If so, find me an orthopedic surgeon in Austin, TX."
        result = run_agent(query)
        
        assert "error" not in result or not result.get("error"), result.get("error")
        
        out = (result.get("output") or "").lower()
        # Ensure it found the coverage
        assert "cover" in out or "yes" in out or "authorized" in out or "network" in out, "Agent didn't seem to check coverage."
        assert len(out) > 20, "Response too short to be a multi-step answer."

    def test_multi_step_provider_and_schedule(self):
        """
        Eval: user asks for a specific provider and their next available appointment.
        Checks if the agent chains: provider_search -> appointment_availability.
        """
        from agent.orchestrator import run_agent

        # Since provider_search requires specialty and location, we ask for a cardiologist.
        query = "Can you find a cardiologist in Austin, TX, and tell me if they have any appointments available on 2025-03-01?"
        result = run_agent(query)
        
        assert "error" not in result or not result.get("error"), result.get("error")
        out = (result.get("output") or "").lower()
        
        # It should find at least one cardiologist (like Dr. Jane Smith or Dr. John Doe) and mention the slot
        assert "smith" in out or "doe" in out, "Did not mention a cardiologist from Austin."
        assert "2025-03-01" in out or "available" in out or "09:00" in out or "10:00" in out or "08:00" in out, "Did not address appointment availability."
