"""
Appointment availability: mock for MVP. Returns available slots for a provider in a date range.
PRE_SEARCH: mock for sprint; production = OpenEMR scheduling API.
"""
import json
import os
import re

from agent.tools.schemas import tool_result

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "appointment_slots.json")


def _load_slots():
    """Load mock appointment slots from JSON."""
    if not os.path.isfile(_DATA_PATH):
        return []
    with open(_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("slots", [])


def _parse_date_range(date_range):
    """
    Parse date_range into (start_date, end_date) as strings YYYY-MM-DD.
    Accepts: "2025-03-01" (single day) or "2025-03-01 to 2025-03-03" (range).
    """
    if not date_range or not isinstance(date_range, str):
        return None, None
    date_range = date_range.strip()
    # Single date
    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_range):
        return date_range, date_range
    # Range: "YYYY-MM-DD to YYYY-MM-DD"
    parts = re.split(r"\s+to\s+", date_range, maxsplit=1)
    if len(parts) == 2 and re.match(r"^\d{4}-\d{2}-\d{2}$", parts[0].strip()) and re.match(r"^\d{4}-\d{2}-\d{2}$", parts[1].strip()):
        return parts[0].strip(), parts[1].strip()
    # Fallback: treat whole string as single date if it looks like YYYY-MM-DD
    if re.search(r"\d{4}-\d{2}-\d{2}", date_range):
        return date_range[:10], date_range[:10]
    return None, None


def appointment_availability(provider_id=None, date_range=None):
    """
    Get available appointment slots for a provider within a date range.
    Returns { success, data: { slots: [...] }?, error? }.
    Mock: filters static list; production would query OpenEMR scheduling API.
    """
    if provider_id is None:
        return tool_result(success=False, error="provider_id is required")
    if date_range is None:
        return tool_result(success=False, error="date_range is required")
    if not isinstance(provider_id, str):
        return tool_result(success=False, error="provider_id must be a string")
    if not isinstance(date_range, str):
        return tool_result(success=False, error="date_range must be a string")

    start_d, end_d = _parse_date_range(date_range)
    if start_d is None:
        return tool_result(success=False, error="date_range must be YYYY-MM-DD or 'YYYY-MM-DD to YYYY-MM-DD'")

    slots = _load_slots()
    filtered = []
    for s in slots:
        if s.get("provider_id") != provider_id:
            continue
        slot_date = (s.get("date") or "")[:10]
        if start_d <= slot_date <= end_d:
            filtered.append(s)

    return tool_result(success=True, data={"slots": filtered})
