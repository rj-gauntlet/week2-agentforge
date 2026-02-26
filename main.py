"""
FastAPI app for the healthcare agent. Run with:
  uvicorn main:app --reload
  uvicorn main:app --host 0.0.0.0 --port 8000  # for deployment
"""
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Form, Response
from pydantic import BaseModel, Field
from twilio.twiml.messaging_response import MessagingResponse

from agent.orchestrator import run_agent

app = FastAPI(
    title="AgentForge Healthcare Agent",
    description="Natural language healthcare assistant: drug interactions, symptoms, providers, appointments, insurance.",
    version="0.1.0",
)


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message")
    history: list[ChatMessage] | None = Field(default=None, description="Previous turns for context")


class ChatResponse(BaseModel):
    output: str = Field(..., description="Agent reply")
    history: list[dict[str, str]] = Field(default_factory=list, description="Updated conversation (role + content)")
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
