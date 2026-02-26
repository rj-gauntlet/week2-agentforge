"""
LangChain tool wrappers for the orchestrator.
Each tool calls our existing Python function and returns a string for the LLM.
"""
import json

from langchain_core.tools import StructuredTool

from agent.tools import (
    drug_interaction_check,
    symptom_lookup,
    provider_search,
    appointment_availability,
    insurance_coverage_check,
)
from agent.tools.procedure_lookup import procedure_lookup


def _result_to_string(result: dict) -> str:
    """Serialize tool result for LLM consumption."""
    if not result.get("success"):
        return f"Error: {result.get('error', 'Unknown error')}"
    return json.dumps(result.get("data", {}), indent=2)


def _drug_interaction_invoke(medications: list[str]) -> str:
    try:
        out = drug_interaction_check(medications=medications)
        return _result_to_string(out)
    except Exception as e:
        return f"Error executing tool: {str(e)}. Please check your arguments and try again."

def _symptom_lookup_invoke(symptoms: list[str]) -> str:
    try:
        out = symptom_lookup(symptoms=symptoms)
        return _result_to_string(out)
    except Exception as e:
        return f"Error executing tool: {str(e)}. Please check your arguments and try again."

def _provider_search_invoke(specialty: str, location: str) -> str:
    try:
        out = provider_search(specialty=specialty, location=location)
        return _result_to_string(out)
    except Exception as e:
        return f"Error executing tool: {str(e)}. Please check your arguments and try again."

def _appointment_availability_invoke(provider_id: str, date_range: str) -> str:
    try:
        out = appointment_availability(provider_id=provider_id, date_range=date_range)
        return _result_to_string(out)
    except Exception as e:
        return f"Error executing tool: {str(e)}. Please check your arguments and try again."

def _insurance_coverage_invoke(procedure_code: str, plan_id: str) -> str:
    try:
        out = insurance_coverage_check(procedure_code=procedure_code, plan_id=plan_id)
        return _result_to_string(out)
    except Exception as e:
        return f"Error executing tool: {str(e)}. Please check your arguments and try again."

def _procedure_lookup_invoke(query: str) -> str:
    try:
        out = procedure_lookup(query=query)
        return _result_to_string(out)
    except Exception as e:
        return f"Error executing tool: {str(e)}. Please check your arguments and try again."


# LangChain tools with descriptions and schemas for the LLM
drug_interaction_tool = StructuredTool.from_function(
    func=_drug_interaction_invoke,
    name="drug_interaction_check",
    description="Check for drug-drug interactions between a list of medications. Input: list of medication names (e.g. aspirin, ibuprofen). Returns interactions and severity (none, minor, major, contraindicated).",
)

symptom_lookup_tool = StructuredTool.from_function(
    func=_symptom_lookup_invoke,
    name="symptom_lookup",
    description="Look up possible conditions and urgency level for given symptoms. Input: list of symptom strings. Returns possible_conditions and urgency (low, medium, high). Does NOT diagnose; always advise user to consult a provider.",
)

provider_search_tool = StructuredTool.from_function(
    func=_provider_search_invoke,
    name="provider_search",
    description="Search for healthcare providers by specialty and location. Input: specialty (e.g. cardiology, pediatrics) and location (e.g. Austin, TX).",
)

appointment_availability_tool = StructuredTool.from_function(
    func=_appointment_availability_invoke,
    name="appointment_availability",
    description="Get available appointment slots for a provider in a date range. Input: provider_id (e.g. prov_001) and date_range (e.g. '2025-03-01' or '2025-03-01 to 2025-03-07').",
)

insurance_coverage_tool = StructuredTool.from_function(
    func=_insurance_coverage_invoke,
    name="insurance_coverage_check",
    description="Check if a procedure is covered under an insurance plan. Input: procedure_code (e.g. 99213) and plan_id (e.g. plan_001). Returns covered (true/false) and details.",
)

procedure_lookup_tool = StructuredTool.from_function(
    func=_procedure_lookup_invoke,
    name="procedure_lookup",
    description="Search for a medical procedure by name to get its CPT code, or search by CPT code to get its name. Input: query (e.g., 'Knee Replacement' or '27447').",
)

def get_langchain_tools():
    """Return list of LangChain tools for the agent."""
    return [
        drug_interaction_tool,
        symptom_lookup_tool,
        provider_search_tool,
        appointment_availability_tool,
        insurance_coverage_tool,
        procedure_lookup_tool,
    ]
