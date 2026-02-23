"""
Hero tool: check drug–drug interactions from a curated static dataset.
PRE_SEARCH: curated static dataset for sprint; production = API (e.g. RxNorm/FDA).
TDD: make tests in tests/unit/test_drug_interaction_check.py pass.
"""
import json
import os

from agent.tools.schemas import tool_result

# Path to curated dataset (relative to project root)
_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "drug_interactions.json")

_severity_order = ("none", "minor", "major", "contraindicated")


def _load_dataset():
    """Load and return the curated drug-interaction pairs. Cached in memory."""
    if not os.path.isfile(_DATA_PATH):
        return []
    with open(_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("pairs", [])


def _normalize(name):
    """Normalize medication name for lookup (lowercase, strip)."""
    if not name or not isinstance(name, str):
        return ""
    return name.strip().lower()


def _pair_key(drug_a, drug_b):
    """Order-independent key for a drug pair."""
    a, b = _normalize(drug_a), _normalize(drug_b)
    if a <= b:
        return (a, b)
    return (b, a)


def _lookup_interactions(medications):
    """
    Look up all pairs in the medication list against the dataset.
    Returns (list of interaction dicts, overall severity).
    """
    pairs_data = _load_dataset()
    # Build lookup: (drug1, drug2) -> { severity, description }
    lookup = {}
    for item in pairs_data:
        drugs = item.get("drugs", [])
        if len(drugs) >= 2:
            key = _pair_key(drugs[0], drugs[1])
            lookup[key] = {
                "severity": item.get("severity", "minor"),
                "description": item.get("description", ""),
            }

    interactions = []
    meds = [_normalize(m) for m in medications if _normalize(m)]
    if len(meds) < 2:
        return [], "none"

    for i in range(len(medications)):
        for j in range(i + 1, len(medications)):
            key = _pair_key(medications[i], medications[j])
            if key in lookup:
                info = lookup[key]
                interactions.append({
                    "drugs": [medications[i], medications[j]],
                    "severity": info["severity"],
                    "description": info["description"],
                })

    if not interactions:
        return [], "none"
    # Overall severity = max severity among interactions
    severities = [s["severity"] for s in interactions]
    overall = "none"
    for sev in _severity_order:
        if sev in severities:
            overall = sev
    return interactions, overall


def drug_interaction_check(medications):
    """
    Check for interactions between a list of medications.
    Returns { success, data: { interactions, severity }?, error? }.
    """
    if medications is None:
        return tool_result(success=False, error="medications must be a list")
    if not isinstance(medications, list):
        return tool_result(success=False, error="medications must be a list")

    if len(medications) == 0:
        return tool_result(
            success=True,
            data={"interactions": [], "severity": "none"},
        )

    interactions, severity = _lookup_interactions(medications)
    return tool_result(
        success=True,
        data={
            "interactions": interactions,
            "severity": severity,
        },
    )
