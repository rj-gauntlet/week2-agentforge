"""
TDD: Tests for provider_search (mock tool for MVP).
Run: pytest tests/unit/test_provider_search.py -v
"""
import pytest

from agent.tools.provider_search import provider_search


@pytest.mark.unit
class TestProviderSearch:
    """Mock tool: returns providers filtered by specialty and location."""

    def test_returns_structured_result(self):
        """Tool must return { success, data: { providers } }; each provider has id, name, specialty, location."""
        result = provider_search(specialty="cardiology", location="Austin")
        assert "success" in result
        assert result["success"] is True
        assert "data" in result
        assert "providers" in result["data"]
        assert isinstance(result["data"]["providers"], list)
        for p in result["data"]["providers"]:
            assert "id" in p
            assert "name" in p
            assert "specialty" in p
            assert "location" in p

    def test_filters_by_specialty(self):
        """Searching for cardiology should return only cardiology providers (or empty)."""
        result = provider_search(specialty="cardiology", location="Austin")
        assert result["success"] is True
        for p in result["data"]["providers"]:
            assert p["specialty"].lower() == "cardiology"

    def test_filters_by_location(self):
        """Searching by location should return only providers in that location (or empty)."""
        result = provider_search(specialty="cardiology", location="Austin")
        assert result["success"] is True
        for p in result["data"]["providers"]:
            assert "austin" in p["location"].lower() or "tx" in p["location"].lower()

    def test_unknown_specialty_returns_empty_list(self):
        """Unknown specialty returns success with empty providers list."""
        result = provider_search(specialty="nonexistent_specialty_xyz", location="Austin")
        assert result["success"] is True
        assert result["data"]["providers"] == []

    def test_invalid_input_returns_graceful_error(self):
        """Missing required params or wrong types return success=False with error."""
        result = provider_search(specialty=None, location="Austin")
        assert result["success"] is False
        assert "error" in result
