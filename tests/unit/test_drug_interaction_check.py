"""
TDD: Tests for drug_interaction_check (hero tool).
Run: pytest tests/unit/test_drug_interaction_check.py -v
Write these first; implementation in agent/tools/drug_interaction_check.py makes them pass.
"""
import pytest

from agent.tools.drug_interaction_check import drug_interaction_check


@pytest.mark.unit
class TestDrugInteractionCheck:
    """Hero tool: returns interactions and severity from curated dataset."""

    def test_returns_structured_result(self):
        """Tool must return { success, data?, error? }; data must have interactions and severity."""
        result = drug_interaction_check(medications=["aspirin", "ibuprofen"])
        assert "success" in result
        assert result["success"] is True
        assert "data" in result
        assert "interactions" in result["data"]
        assert "severity" in result["data"]
        assert result["data"]["severity"] in ("none", "minor", "major", "contraindicated")

    def test_known_interaction_returns_major_or_higher(self):
        """A known dangerous pair (e.g. warfarin + aspirin) should report at least 'major' or contraindicated."""
        result = drug_interaction_check(medications=["warfarin", "aspirin"])
        assert result["success"] is True
        assert result["data"]["severity"] in ("major", "contraindicated")
        assert len(result["data"]["interactions"]) >= 1

    def test_single_medication_returns_no_interaction(self):
        """Single medication should return no interaction (severity 'none')."""
        result = drug_interaction_check(medications=["lisinopril"])
        assert result["success"] is True
        assert result["data"]["severity"] == "none"
        assert result["data"]["interactions"] == [] or "no interaction" in str(result["data"]).lower()

    def test_empty_list_returns_error_or_safe_result(self):
        """Empty medication list should not crash; return error or valid result."""
        result = drug_interaction_check(medications=[])
        assert "success" in result
        # Either success with empty interactions or success=False with error
        if result["success"]:
            assert result["data"]["severity"] == "none" or result["data"]["interactions"] == []
        else:
            assert "error" in result

    def test_invalid_input_returns_graceful_error(self):
        """Non-list or bad input should return success=False with error message."""
        result = drug_interaction_check(medications=None)
        assert result["success"] is False
        assert "error" in result
