"""
Insurance coverage check: mock for MVP. Returns whether a procedure is covered under a plan.
PRE_SEARCH: mock for sprint; production = OpenEMR billing / clearinghouse.
"""
import json
import os

from agent.tools.schemas import tool_result

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "insurance_coverage.json")


def _load_coverage():
    """Load procedure_code + plan_id -> coverage from JSON."""
    if not os.path.isfile(_DATA_PATH):
        return []
    with open(_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("coverage", [])


def insurance_coverage_check(procedure_code=None, plan_id=None):
    """
    Check if a procedure is covered under a plan.
    Returns { success, data: { covered, details? }?, error? }.
    """
    if procedure_code is None:
        return tool_result(success=False, error="procedure_code is required")
    if plan_id is None:
        return tool_result(success=False, error="plan_id is required")
    if not isinstance(procedure_code, str):
        return tool_result(success=False, error="procedure_code must be a string")
    if not isinstance(plan_id, str):
        return tool_result(success=False, error="plan_id must be a string")

    procedure_code = procedure_code.strip()
    plan_id = plan_id.strip()
    coverage_list = _load_coverage()

    for row in coverage_list:
        if row.get("procedure_code") == procedure_code and row.get("plan_id") == plan_id:
            return tool_result(
                success=True,
                data={
                    "covered": row.get("covered", False),
                    "details": row.get("details"),
                },
            )

    return tool_result(
        success=True,
        data={
            "covered": False,
            "details": "No coverage information found for this procedure and plan.",
        },
    )
