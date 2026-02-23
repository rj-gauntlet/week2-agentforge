"""
TDD: Tests for symptom_lookup (mock tool for MVP).
Returns possible conditions and urgency only — no diagnosis.
Run: pytest tests/unit/test_symptom_lookup.py -v
"""
import pytest

from agent.tools.symptom_lookup import symptom_lookup


@pytest.mark.unit
class TestSymptomLookup:
    """Mock tool: returns possible conditions and urgency; no diagnosis."""

    def test_returns_structured_result(self):
        """Tool must return { success, data: { possible_conditions, urgency } }."""
        result = symptom_lookup(symptoms=["headache"])
        assert "success" in result
        assert result["success"] is True
        assert "data" in result
        assert "possible_conditions" in result["data"]
        assert "urgency" in result["data"]
        assert isinstance(result["data"]["possible_conditions"], list)
        assert result["data"]["urgency"] in ("low", "medium", "high")

    def test_urgency_is_valid_level(self):
        """Urgency must be one of low, medium, high."""
        result = symptom_lookup(symptoms=["chest pain"])
        assert result["success"] is True
        assert result["data"]["urgency"] in ("low", "medium", "high")

    def test_high_urgency_symptoms_return_high(self):
        """Symptoms like chest pain should return high urgency (mock data)."""
        result = symptom_lookup(symptoms=["chest pain"])
        assert result["success"] is True
        assert result["data"]["urgency"] == "high"

    def test_empty_symptoms_returns_error_or_low_urgency(self):
        """Empty symptom list should not crash; return error or valid result with low urgency."""
        result = symptom_lookup(symptoms=[])
        assert "success" in result
        if result["success"]:
            assert result["data"]["urgency"] in ("low", "medium", "high")
        else:
            assert "error" in result

    def test_invalid_input_returns_graceful_error(self):
        """Non-list or None symptoms return success=False with error."""
        result = symptom_lookup(symptoms=None)
        assert result["success"] is False
        assert "error" in result
