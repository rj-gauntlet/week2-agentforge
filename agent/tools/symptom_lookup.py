"""
Symptom lookup: mock for MVP. Returns possible conditions and urgency only — no diagnosis.
PRE_SEARCH: mock for sprint; production = clinical knowledge base.
"""
import json
import os

from agent.tools.schemas import tool_result

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "symptom_lookup.json")
_URGENCY_ORDER = ("low", "medium", "high")


def _load_symptoms():
    """Load symptom -> conditions + urgency from JSON."""
    if not os.path.isfile(_DATA_PATH):
        return []
    with open(_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("symptoms", [])


def _normalize(s):
    """Normalize string for lookup."""
    return (s or "").strip().lower()


def symptom_lookup(symptoms=None):
    """
    Look up possible conditions and urgency for given symptoms. No diagnosis.
    Returns { success, data: { possible_conditions, urgency }?, error? }.
    """
    if symptoms is None:
        return tool_result(success=False, error="symptoms must be a list")
    if not isinstance(symptoms, list):
        return tool_result(success=False, error="symptoms must be a list")

    if len(symptoms) == 0:
        return tool_result(
            success=True,
            data={"possible_conditions": [], "urgency": "low"},
        )

    symptom_data = _load_symptoms()
    lookup = {_normalize(s["symptom"]): s for s in symptom_data}

    possible_conditions = []
    max_urgency = "low"
    for sym in symptoms:
        key = _normalize(sym)
        if key in lookup:
            entry = lookup[key]
            possible_conditions.extend(entry.get("possible_conditions", []))
            u = entry.get("urgency", "low")
            if _URGENCY_ORDER.index(u) > _URGENCY_ORDER.index(max_urgency):
                max_urgency = u

    # Dedupe and cap conditions
    seen = set()
    unique = []
    for c in possible_conditions:
        if c not in seen:
            seen.add(c)
            unique.append(c)

    return tool_result(
        success=True,
        data={
            "possible_conditions": unique if unique else ["No matching information in lookup; consult a provider."],
            "urgency": max_urgency,
            "can_diagnose": False,
            "requires_provider_consultation": True
        },
    )
