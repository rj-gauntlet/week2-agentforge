"""
Provider search: mock for MVP. Returns providers filtered by specialty and location.
PRE_SEARCH: mock for sprint; production = OpenEMR provider directory / FHIR.
"""
import json
import os

from agent.tools.schemas import tool_result

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "providers.json")


def _load_providers():
    """Load mock provider list from JSON."""
    if not os.path.isfile(_DATA_PATH):
        return []
    with open(_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("providers", [])


def provider_search(specialty=None, location=None):
    """
    Search for providers by specialty and location.
    Returns { success, data: { providers: [...] }?, error? }.
    Mock: filters static list; production would query OpenEMR FHIR.
    """
    if specialty is None:
        return tool_result(success=False, error="specialty is required")
    if location is None:
        return tool_result(success=False, error="location is required")
    if not isinstance(specialty, str):
        return tool_result(success=False, error="specialty must be a string")
    if not isinstance(location, str):
        return tool_result(success=False, error="location must be a string")

    providers = _load_providers()
    specialty_n = (specialty or "").strip().lower()
    location_n = (location or "").strip().lower()

    filtered = []
    for p in providers:
        if specialty_n and p.get("specialty", "").lower() != specialty_n:
            continue
        if location_n:
            loc = (p.get("location") or "").lower()
            if location_n not in loc:
                continue
        filtered.append(p)

    return tool_result(success=True, data={"providers": filtered})
