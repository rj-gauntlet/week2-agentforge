"""
Lab result interpretation: compares patient lab values against standard reference ranges.
Returns whether each value is normal, low, or high, along with reference ranges.
"""
from agent.tools.schemas import tool_result

# Standard reference ranges (adult, general)
# Ranges are typically min to max. If min is None, there is no lower bound.
REFERENCE_RANGES = {
    "glucose": {"min": 70.0, "max": 99.0, "unit": "mg/dL", "description": "Fasting blood sugar. High levels may indicate diabetes."},
    "a1c": {"min": 0.0, "max": 5.6, "unit": "%", "description": "Average blood sugar over 2-3 months."},
    "cholesterol_total": {"min": 0.0, "max": 199.0, "unit": "mg/dL", "description": "Total cholesterol in the blood."},
    "hdl": {"min": 40.0, "max": 1000.0, "unit": "mg/dL", "description": "High-density lipoprotein (good cholesterol). Low levels are a risk factor for heart disease."},
    "ldl": {"min": 0.0, "max": 99.0, "unit": "mg/dL", "description": "Low-density lipoprotein (bad cholesterol)."},
    "triglycerides": {"min": 0.0, "max": 149.0, "unit": "mg/dL", "description": "A type of fat found in your blood."},
    "hemoglobin": {"min": 12.0, "max": 17.5, "unit": "g/dL", "description": "Protein in red blood cells that carries oxygen. Varies slightly by gender."},
    "wbc": {"min": 4.5, "max": 11.0, "unit": "10^9/L", "description": "White blood cell count. High levels may indicate infection."},
    "platelets": {"min": 150.0, "max": 450.0, "unit": "10^9/L", "description": "Cell fragments that help with blood clotting."},
    "sodium": {"min": 135.0, "max": 145.0, "unit": "mEq/L", "description": "An electrolyte crucial for nerve and muscle function."},
    "potassium": {"min": 13.5, "max": 5.2, "unit": "mEq/L", "description": "Helps with nerve function and muscle contraction. (Note: standard is 3.5 to 5.2)"},
    "creatinine": {"min": 0.6, "max": 1.2, "unit": "mg/dL", "description": "Waste product filtered by kidneys. High levels may indicate reduced kidney function."}
}

# Fix potassium standard range
REFERENCE_RANGES["potassium"]["min"] = 3.5

def _normalize_key(key: str) -> str:
    key = key.lower().replace(" ", "_")
    if key in ["hba1c", "hemoglobin_a1c"]: return "a1c"
    if key in ["cholesterol"]: return "cholesterol_total"
    if key in ["wbc_count", "white_blood_cells"]: return "wbc"
    if key in ["rbc", "red_blood_cells"]: return "hemoglobin" # Simplification
    return key

def lab_result_interpretation(lab_values: dict) -> dict:
    """
    Interpret a dictionary of lab results.
    Input format: {"glucose": 110, "hdl": 35}
    Returns { success, data: { interpretations: [...] }?, error? }
    """
    if lab_values is None or not isinstance(lab_values, dict):
        return tool_result(success=False, error="lab_values must be a dictionary of test names and numerical values.")

    interpretations = []
    
    for raw_test_name, value in lab_values.items():
        test_key = _normalize_key(raw_test_name)
        
        try:
            val_float = float(value)
        except (ValueError, TypeError):
            interpretations.append({
                "test_name": raw_test_name,
                "status": "error",
                "message": f"Could not parse value '{value}' as a number."
            })
            continue

        if test_key in REFERENCE_RANGES:
            ref = REFERENCE_RANGES[test_key]
            
            if val_float < ref["min"]:
                status = "low"
            elif val_float > ref["max"]:
                status = "high"
            else:
                status = "normal"
                
            interpretations.append({
                "test_name": raw_test_name,
                "value": val_float,
                "unit": ref["unit"],
                "status": status,
                "reference_range": f"{ref['min']} - {ref['max']}",
                "description": ref["description"]
            })
        else:
            interpretations.append({
                "test_name": raw_test_name,
                "value": val_float,
                "status": "unknown",
                "message": "Reference range not available for this test in the current database."
            })

    return tool_result(success=True, data={"interpretations": interpretations})
