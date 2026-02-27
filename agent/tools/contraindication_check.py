"""
Contraindication check: mock for MVP. Returns whether a procedure is contraindicated 
given a patient's conditions and medications.
"""
import json
import os

from agent.tools.schemas import tool_result

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "contraindications.json")

def _load_data():
    if not os.path.isfile(_DATA_PATH):
        return []
    with open(_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("contraindications", [])

def _normalize(text):
    return text.strip().lower()

def contraindication_check(procedure_code: str, patient_conditions: list = None, patient_medications: list = None):
    """
    Check if a procedure is contraindicated based on patient conditions and medications.
    Returns { success, data: { safe: bool, flagged_issues: list, reason: str }?, error? }
    """
    if not procedure_code:
        return tool_result(success=False, error="procedure_code is required")
        
    patient_conditions = [_normalize(c) for c in (patient_conditions or [])]
    patient_medications = [_normalize(m) for m in (patient_medications or [])]
    
    data = _load_data()
    
    # Find the procedure
    procedure_data = None
    for item in data:
        if item.get("procedure_code") == str(procedure_code):
            procedure_data = item
            break
            
    if not procedure_data:
        return tool_result(
            success=True, 
            data={
                "safe": True, 
                "flagged_issues": [], 
                "reason": f"No contraindication data found for procedure code {procedure_code}."
            }
        )
        
    flagged_issues = []
    
    # Check conditions
    for condition in patient_conditions:
        if condition in procedure_data.get("flagged_conditions", []):
            flagged_issues.append(f"Condition: {condition}")
            
    # Check medications
    for med in patient_medications:
        if med in procedure_data.get("flagged_medications", []):
            flagged_issues.append(f"Medication: {med}")
            
    if flagged_issues:
        return tool_result(
            success=True,
            data={
                "safe": False,
                "procedure_name": procedure_data.get("procedure_name"),
                "flagged_issues": flagged_issues,
                "reason": procedure_data.get("reason", "Contraindication detected.")
            }
        )
        
    return tool_result(
        success=True,
        data={
            "safe": True,
            "procedure_name": procedure_data.get("procedure_name"),
            "flagged_issues": [],
            "reason": "No known contraindications found for the provided conditions and medications."
        }
    )
