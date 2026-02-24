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

Rules:
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


def run_agent(
    query: str,
    chat_history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """
    Run the agent on a user query with optional conversation history.
    Returns { "output": str, "messages": list (updated with this turn), "error": str? }.
    """
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

    return {
        "output": output or "I couldn't generate a response. Please try again.",
        "messages": out_messages,
    }
