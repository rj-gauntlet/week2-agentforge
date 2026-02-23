"""
TDD: Tests for insurance_coverage_check (mock tool for MVP).
Run: pytest tests/unit/test_insurance_coverage_check.py -v
"""
import pytest

from agent.tools.insurance_coverage_check import insurance_coverage_check


@pytest.mark.unit
class TestInsuranceCoverageCheck:
    """Mock tool: returns coverage details for a procedure under a plan."""

    def test_returns_structured_result(self):
        """Tool must return { success, data: { covered, details? } }."""
        result = insurance_coverage_check(procedure_code="99213", plan_id="plan_001")
        assert "success" in result
        assert result["success"] is True
        assert "data" in result
        assert "covered" in result["data"]
        assert isinstance(result["data"]["covered"], bool)

    def test_known_procedure_plan_returns_coverage(self):
        """Known procedure + plan returns covered True or False with details."""
        result = insurance_coverage_check(procedure_code="99213", plan_id="plan_001")
        assert result["success"] is True
        assert "covered" in result["data"]
        # Optional: details (e.g. copay, prior_auth)
        if "details" in result["data"]:
            assert isinstance(result["data"]["details"], (dict, str, type(None)))

    def test_unknown_procedure_or_plan_returns_graceful_result(self):
        """Unknown procedure_code or plan_id returns success with covered=False or error message."""
        result = insurance_coverage_check(procedure_code="unknown_xyz", plan_id="plan_001")
        assert result["success"] is True
        assert "covered" in result["data"]

    def test_invalid_input_returns_graceful_error(self):
        """Missing or invalid params return success=False with error."""
        result = insurance_coverage_check(procedure_code=None, plan_id="plan_001")
        assert result["success"] is False
        assert "error" in result
