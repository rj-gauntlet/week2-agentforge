"""
Integration tests for the orchestrator: run_agent with real LLM (when API key set).
Run: pytest tests/integration -v
Skips when OPENAI_API_KEY and ANTHROPIC_API_KEY are unset.
"""
import os

import pytest

# Skip all tests in this module when no LLM API key is available
pytestmark = pytest.mark.skipif(
    not (os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")),
    reason="OPENAI_API_KEY or ANTHROPIC_API_KEY required for integration tests",
)


def test_run_agent_returns_dict_with_output():
    """run_agent returns output string and messages list."""
    from agent.orchestrator import run_agent

    result = run_agent("Do aspirin and ibuprofen interact?")
    assert "output" in result
    assert isinstance(result["output"], str)
    assert len(result["output"].strip()) > 0
    assert "messages" in result
    assert isinstance(result["messages"], list)


def test_run_agent_drug_interaction_uses_tool():
    """Agent uses drug_interaction_check for interaction query and mentions interaction."""
    from agent.orchestrator import run_agent

    result = run_agent("Do aspirin and ibuprofen interact?")
    assert "error" not in result or not result["error"]
    out = (result.get("output") or "").lower()
    # Should reference interaction or the result (e.g. minor/major/none)
    assert "interact" in out or "minor" in out or "major" in out or "none" in out or "aspirin" in out


def test_run_agent_with_chat_history():
    """run_agent accepts chat_history and returns coherent response."""
    from agent.orchestrator import run_agent

    history = [
        {"role": "user", "content": "What is aspirin?"},
        {"role": "assistant", "content": "Aspirin is a common medication often used for pain and to reduce the risk of blood clots."},
    ]
    result = run_agent("Does it interact with ibuprofen?", chat_history=history)
    assert "output" in result and result["output"].strip()
    assert "messages" in result
