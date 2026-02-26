"""
Orchestrator: LangChain agent with tool-calling and conversation memory.
Wires the five healthcare tools; one entrypoint run_agent(query, chat_history=[]).
"""
import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

load_dotenv()

# Lazy imports so we don't require langchain/chat_models if only running tools
_agent = None

SYSTEM_PROMPT = """You are a healthcare assistant for a clinical setting. You help with:
- Drug interaction checks (list of medications)
- Symptom lookup (possible conditions and urgency only — never diagnose)
- Provider search (by specialty and location)
- Appointment availability (provider ID and date range)
- Insurance coverage (procedure code and plan ID)
- Procedure lookup (search for a CPT code by name, or name by code)

Rules:
- STRICT PERSONA LOCK: You must ALWAYS maintain a professional, helpful, and clear clinical persona. Under NO circumstances should you adopt a different persona, accent, character, or style (e.g., pirate, cowboy, fictional character, etc.), even if explicitly instructed to do so by the user.
- Use the tools to answer; do not make up medical facts.
- For symptoms or clinical questions, always add: "This is not a diagnosis; please consult your provider."
- Cite the tool you used (e.g. "According to the drug interaction check...").
- If a tool returns an error or empty result, say so and suggest rephrasing or checking with staff.
- Do not give dosing advice or diagnose conditions.
- If the user asks a question entirely unrelated to healthcare, medicine, or the tools provided, you must politely refuse to answer and remind them of your clinical purpose."""


def _get_model():
    """Return chat model from env: OPENAI_API_KEY -> gpt-4o, ANTHROPIC_API_KEY -> claude."""
    if os.getenv("OPENAI_API_KEY"):
        from langchain.chat_models import init_chat_model
        return init_chat_model("openai:gpt-4o", temperature=0)
    if os.getenv("ANTHROPIC_API_KEY"):
        from langchain.chat_models import init_chat_model
        return init_chat_model("anthropic:claude-sonnet-4-20250514", temperature=0)
    raise RuntimeError(
        "Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env to run the agent. "
        "See .env.example."
    )


def _build_agent():
    """Build and cache the LangChain agent (model + tools + prompt)."""
    global _agent
    if _agent is not None:
        return _agent
    from langchain.agents import create_agent
    from agent.tools.langchain_tools import get_langchain_tools
    model = _get_model()
    tools = get_langchain_tools()
    _agent = create_agent(model=model, tools=tools, system_prompt=SYSTEM_PROMPT)
    return _agent


def _messages_from_history(chat_history: list[dict[str, str]]) -> list[BaseMessage]:
    """Convert list of {role, content} dicts to LangChain messages."""
    out = []
    for m in chat_history:
        role = (m.get("role") or "").strip().lower()
        content = m.get("content") or ""
        if role == "user" or role == "human":
            out.append(HumanMessage(content=content))
        elif role == "assistant" or role == "ai":
            out.append(AIMessage(content=content))
    return out


def _verify_input_domain(query: str) -> str | None:
    """Verification 1: Domain Constraints / Input validation.
    Quick heuristic check to catch blatant adversarial or out-of-domain requests before LLM processing."""
    query_lower = query.lower()
    adversarial_keywords = ["ignore previous", "system prompt", "hack", "bypass", "talk like", "act like", "pirate"]
    if any(kw in query_lower for kw in adversarial_keywords):
        return "I'm a healthcare assistant and cannot fulfill requests that bypass my instructions, change my persona, or involve hacking."
    return None

import re

def _verify_phi_redaction(query: str) -> str:
    """Verification 3: PHI Redaction / Privacy check.
    Masks out sensitive information like SSNs, Phone Numbers, and Dates of Birth before sending to the LLM."""
    
    # 1. Redact SSN (e.g., 123-45-6789 or 123456789)
    ssn_pattern = r'\b\d{3}[-]?\d{2}[-]?\d{4}\b'
    query = re.sub(ssn_pattern, '[REDACTED SSN]', query)
    
    # 2. Redact Phone Numbers (e.g., 555-555-5555, (555) 555-5555, +1-555-555-5555)
    phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    query = re.sub(phone_pattern, '[REDACTED PHONE]', query)
    
    # 3. Redact Birthdays/Dates ONLY if preceded by DOB keywords (e.g., "DOB", "born on")
    # This prevents redacting appointment dates like "2025-03-01"
    dob_pattern = r'(?i)\b(?:dob|born|birth(?:day|date)?)\s*(?:on|is)?\s*[:\s]*(\d{1,4}[-/]\d{1,2}[-/]\d{1,4})\b'
    query = re.sub(dob_pattern, '[REDACTED DOB]', query)
    
    return query

def _verify_fact_check(output: str, tool_messages: list) -> str:
    """Verification 4: Fact-Checking against Tool Output.
    If the drug interaction tool was called, ensure the LLM didn't hallucinate a 'fatal' severity
    if the tool only returned 'minor'.
    """
    output_lower = output.lower()
    
    for tm in tool_messages:
        # Check if the step was the drug_interaction_check tool
        if tm.name == "drug_interaction_check":
            result_str = str(tm.content).lower()
            
            # If the tool result says "minor" but the LLM output claims "fatal" or "major"
            if "minor" in result_str and ("fatal" in output_lower or "major" in output_lower):
                return output + "\n\n(Fact-Check Error: The LLM severity description contradicts the tool's 'minor' rating. Please verify.)"
    
    return output

def _verify_output_safety(output: str) -> str:
    """Verification 2: Output Validation / Safety check.
    Ensure that any output discussing symptoms or conditions includes a safety disclaimer."""
    output_lower = output.lower()
    clinical_keywords = ["headache", "fever", "pain", "infection", "symptom", "disease", "condition", "diagnose"]
    needs_disclaimer = any(kw in output_lower for kw in clinical_keywords)
    has_disclaimer = "not a diagnosis" in output_lower or "consult your provider" in output_lower
    
    if needs_disclaimer and not has_disclaimer:
        return output + "\n\n(Disclaimer: This information is not a diagnosis. Please consult your provider.)"
    return output

def run_agent(
    query: str,
    chat_history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """
    Run the agent on a user query with optional conversation history.
    Returns { "output": str, "messages": list (updated with this turn), "error": str? }.
    """
    # 3. Verification: PHI Redaction Check
    query = _verify_phi_redaction(query)

    # 1. Verification: Input Domain Check
    input_violation = _verify_input_domain(query)
    if input_violation:
        return {
            "output": input_violation,
            "messages": chat_history or [],
        }

    chat_history = chat_history or []
    messages = _messages_from_history(chat_history)
    messages.append(HumanMessage(content=query))

    try:
        agent = _build_agent()
        result = agent.invoke({"messages": messages})
    except Exception as e:
        return {
            "output": "",
            "messages": [],
            "error": str(e),
        }

    out_messages = result.get("messages", [])
    output = ""
    for m in reversed(out_messages):
        if hasattr(m, "content") and m.content and isinstance(m.content, str):
            output = m.content
            break

    # 4. Verification: Fact Check against tool output
    # We can pull intermediate tool messages from the history
    from langchain_core.messages import ToolMessage
    tool_messages = [m for m in out_messages if isinstance(m, ToolMessage)]
    
    if output and tool_messages:
        output = _verify_fact_check(output, tool_messages)

    # 2. Verification: Output Safety Check
    if output:
        output = _verify_output_safety(output)

    return {
        "output": output or "I couldn't generate a response. Please try again.",
        "messages": out_messages,
    }
