"""
TDD: Tests for appointment_availability (mock tool for MVP).
Run: pytest tests/unit/test_appointment_availability.py -v
"""
import pytest

from agent.tools.appointment_availability import appointment_availability


@pytest.mark.unit
class TestAppointmentAvailability:
    """Mock tool: returns available slots for a provider in a date range."""

    def test_returns_structured_result(self):
        """Tool must return { success, data: { slots } }; each slot has provider_id, date, start_time, end_time."""
        result = appointment_availability(provider_id="prov_001", date_range="2025-03-01")
        assert "success" in result
        assert result["success"] is True
        assert "data" in result
        assert "slots" in result["data"]
        assert isinstance(result["data"]["slots"], list)
        for slot in result["data"]["slots"]:
            assert "provider_id" in slot
            assert "date" in slot
            assert "start_time" in slot
            assert "end_time" in slot

    def test_filters_by_provider_id(self):
        """Slots returned must be for the requested provider only."""
        result = appointment_availability(provider_id="prov_001", date_range="2025-03-01")
        assert result["success"] is True
        for slot in result["data"]["slots"]:
            assert slot["provider_id"] == "prov_001"

    def test_filters_by_date_range(self):
        """Slots must fall within the requested date range."""
        result = appointment_availability(provider_id="prov_001", date_range="2025-03-01 to 2025-03-03")
        assert result["success"] is True
        for slot in result["data"]["slots"]:
            # date should be in range (e.g. YYYY-MM-DD string)
            assert "2025-03" in slot["date"]

    def test_unknown_provider_returns_empty_slots(self):
        """Unknown provider_id returns success with empty slots list."""
        result = appointment_availability(provider_id="unknown_provider_xyz", date_range="2025-03-01")
        assert result["success"] is True
        assert result["data"]["slots"] == []

    def test_invalid_input_returns_graceful_error(self):
        """Missing or invalid params return success=False with error."""
        result = appointment_availability(provider_id=None, date_range="2025-03-01")
        assert result["success"] is False
        assert "error" in result
