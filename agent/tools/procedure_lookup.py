import json
import os

from agent.tools.schemas import tool_result

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "procedures.json")

def _load_procedures():
    """Load procedure -> code mapping from JSON."""
    if not os.path.isfile(_DATA_PATH):
        return []
    with open(_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("procedures", [])

def procedure_lookup(query: str):
    """
    Search for a medical procedure by name to get its CPT code, or search by code to get its name.
    Returns { success, data: { procedures: list }, error? }
    """
    if not query or not isinstance(query, str):
        return tool_result(success=False, error="query must be a non-empty string")

    procedures_data = _load_procedures()
    query_lower = query.strip().lower()

    results = []
    for proc in procedures_data:
        code = proc.get("code", "").lower()
        name = proc.get("name", "").lower()
        desc = proc.get("description", "").lower()
        
        # Check for exact code match first
        if query_lower == code:
            results.append(proc)
            continue
            
        # Then check for partial name/description match
        if query_lower in name or query_lower in desc:
            results.append(proc)

    if not results:
        return tool_result(
            success=True, 
            data={"procedures": [], "message": f"No procedure found matching '{query}'"}
        )

    return tool_result(
        success=True,
        data={
            "procedures": results
        }
    )
