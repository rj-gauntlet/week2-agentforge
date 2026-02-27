"""
Appointment availability: mock for MVP. Returns available slots for a provider in a date range.
PRE_SEARCH: mock for sprint; production = OpenEMR scheduling API.
"""
import re
from datetime import datetime, timedelta

from agent.tools.schemas import tool_result


def _generate_dynamic_slots():
    """Generate dynamic mock appointment slots for a 14-day window from today."""
    slots = []
    today = datetime.now()
    
    # Providers and their typical schedules
    schedules = {
        "prov_001": [("09:00", "09:30"), ("10:00", "10:30"), ("14:00", "14:30")],
        "prov_002": [("08:00", "08:30"), ("15:00", "15:30")],
        "prov_003": [("09:00", "09:30"), ("11:00", "11:30")]
    }

    for day_offset in range(14):
        current_day = today + timedelta(days=day_offset)
        # Skip weekends for realism
        if current_day.weekday() >= 5:
            continue
            
        date_str = current_day.strftime("%Y-%m-%d")
        
        for provider_id, times in schedules.items():
            for start_time, end_time in times:
                # Add a bit of pseudo-randomness: skip some slots based on day
                # So it's not totally uniform, just to make it more realistic
                if (day_offset + hash(provider_id + start_time)) % 3 == 0:
                    continue
                    
                slots.append({
                    "provider_id": provider_id,
                    "date": date_str,
                    "start_time": start_time,
                    "end_time": end_time
                })
                
    return slots


def _parse_date_range(date_range):
    """
    Parse date_range into (start_date, end_date) as strings YYYY-MM-DD.
    Accepts: "YYYY-MM-DD" (single day) or "YYYY-MM-DD to YYYY-MM-DD" (range).
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
    Mock: filters dynamically generated schedule over the next 14 days.
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

    slots = _generate_dynamic_slots()
    filtered = []
    for s in slots:
        if s.get("provider_id") != provider_id:
            continue
        slot_date = (s.get("date") or "")[:10]
        if start_d <= slot_date <= end_d:
            filtered.append(s)

    return tool_result(
        success=True,
        data={"slots": filtered, "available": len(filtered) > 0},
    )
