"""
FastAPI app for the healthcare agent. Run with:
  uvicorn main:app --reload
  uvicorn main:app --host 0.0.0.0 --port 8000  # for deployment
"""
import os
from typing import Any, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from fastapi import FastAPI, HTTPException, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from twilio.twiml.messaging_response import MessagingResponse

from agent.orchestrator import run_agent

# Allowed origins for CORS (dev + dynamic from env)
env_origins = os.getenv("CORS_ORIGINS", "")
CORS_ORIGINS = [o.strip() for o in env_origins.split(",")] if env_origins else [
    "http://localhost:5173", "http://localhost:5174", "http://localhost:5175",
    "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:5175",
]


class CORSPreflightMiddleware(BaseHTTPMiddleware):
    """Handle OPTIONS preflight before router so CORS always works."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method == "OPTIONS" and request.url.path in ("/chat", "/feedback"):
            origin = request.headers.get("origin", "")
            allow = origin if origin in CORS_ORIGINS else (CORS_ORIGINS[0] if CORS_ORIGINS else "*")
            return Response(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": allow,
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Max-Age": "86400",
                },
            )
        return await call_next(request)


app = FastAPI(
    title="AgentForge Healthcare Agent",
    description="Natural language healthcare assistant: drug interactions, symptoms, providers, appointments, insurance.",
    version="0.1.0",
)

# Add CORSMiddleware first, then preflight so preflight runs first (last added = first to run)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CORSPreflightMiddleware)


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message")
    history: list[ChatMessage] | None = Field(default=None, description="Previous turns for context")


class ToolUsed(BaseModel):
    name: str = Field(..., description="Tool name")
    args: dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    output: Any = Field(default=None, description="Tool output (parsed or raw string)")


class ChatResponse(BaseModel):
    output: str = Field(..., description="Agent reply")
    history: list[dict[str, str]] = Field(default_factory=list, description="Updated conversation (role + content)")
    tools_used: list[ToolUsed] = Field(default_factory=list, description="Tools invoked this turn (for UI expanders)")
    error: str | None = Field(default=None, description="Error message if something went wrong")


def _messages_to_history(messages: list[Any]) -> list[dict[str, str]]:
    """Convert LangChain messages to JSON-safe list of {role, content}."""
    out = []
    for m in messages:
        content = getattr(m, "content", None) or ""
        if not isinstance(content, str):
            continue
        name = type(m).__name__
        if "Human" in name or "user" in str(name).lower():
            role = "user"
        elif "AI" in name or "assistant" in str(name).lower():
            role = "assistant"
        else:
            continue
        out.append({"role": role, "content": content})
    return out


def _extract_tools_used(messages: list[Any]) -> list[dict[str, Any]]:
    """Extract tool calls and outputs from agent messages for UI display."""
    from langchain_core.messages import ToolMessage

    tool_outputs: dict[str, Any] = {}
    for m in messages:
        if getattr(m, "type", None) == "tool" or type(m).__name__ == "ToolMessage":
            tid = getattr(m, "tool_call_id", None)
            if tid:
                raw = getattr(m, "content", None)
                try:
                    import json
                    tool_outputs[tid] = json.loads(raw) if isinstance(raw, str) else raw
                except Exception:
                    tool_outputs[tid] = raw

    tools_used: list[dict[str, Any]] = []
    for m in messages:
        if not getattr(m, "tool_calls", None):
            continue
        for tc in m.tool_calls:
            tid = tc.get("id")
            raw_out = tool_outputs.get(tid, "No output recorded.")
            tools_used.append({
                "name": tc.get("name", ""),
                "args": tc.get("args") or {},
                "output": raw_out,
            })
    return tools_used


@app.options("/chat")
@app.options("/feedback")
def cors_preflight(request: Request):
    """Handle CORS preflight so browser requests succeed."""
    origin = request.headers.get("origin", "")
    allowed = [
        "http://localhost:5173", "http://localhost:5174", "http://localhost:5175",
        "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:5175",
    ]
    allow_origin = origin if origin in allowed else allowed[0]
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": allow_origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "86400",
        },
    )


@app.get("/")
def root():
    """Root: point to the main endpoints."""
    return {
        "app": "AgentForge Healthcare Agent",
        "docs": "/docs",
        "health": "/health",
        "chat": "POST /chat with JSON body: {\"message\": \"...\"}",
        "feedback": "POST /feedback"
    }

class FeedbackRequest(BaseModel):
    message_id: str = Field(..., description="ID or turn index of the message")
    rating: str = Field(..., description="'thumbs_up' or 'thumbs_down'")
    comments: str | None = Field(default=None, description="Optional user feedback comments")

@app.post("/feedback")
def collect_feedback(feedback: FeedbackRequest):
    """Collect user feedback for observability and evaluation."""
    # In a real app, this would be saved to a database or sent to LangSmith / Braintrust.
    return {"status": "success", "recorded_rating": feedback.rating}

@app.get("/health")
def health():
    """Liveness/readiness for deployment."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Send a message to the agent. Optionally pass previous turns in history for context.
    Requires OPENAI_API_KEY or ANTHROPIC_API_KEY in the environment.
    """
    history = None
    if request.history:
        history = [{"role": m.role, "content": m.content} for m in request.history]

    result = run_agent(request.message, chat_history=history)

    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])

    return ChatResponse(
        output=result["output"],
        history=_messages_to_history(result.get("messages", [])),
        tools_used=[ToolUsed(**t) for t in _extract_tools_used(result.get("messages", []))],
        error=result.get("error"),
    )


@app.post("/sms")
async def sms_reply(Body: str = Form(...)):
    """
    Webhook for Twilio SMS and WhatsApp.
    Twilio sends form data including `Body` (the text message).
    Returns an XML TwiML response.
    """
    # Call our agent with the incoming text
    result = run_agent(query=Body, chat_history=None)
    
    # Extract the agent's response or an error message
    if result.get("error"):
        reply_text = f"System Error: {result['error']}"
    else:
        reply_text = result.get("output", "I'm sorry, I encountered an error processing your request.")
        
    # Build the Twilio XML response
    resp = MessagingResponse()
    resp.message(reply_text)
    
    # Return raw XML so Twilio understands it
    return Response(content=str(resp), media_type="application/xml")
