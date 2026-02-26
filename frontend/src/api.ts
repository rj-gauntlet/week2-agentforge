const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ToolUsed {
  name: string;
  args: Record<string, unknown>;
  output: unknown;
}

export interface ChatResponse {
  output: string;
  history: Array<{ role: string; content: string }>;
  tools_used: ToolUsed[];
  error: string | null;
}

export async function sendMessage(
  message: string,
  history: ChatMessage[]
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      history: history.map((m) => ({ role: m.role, content: m.content })),
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? res.statusText);
  }
  return res.json();
}

export async function sendFeedback(messageId: string, rating: "thumbs_up" | "thumbs_down"): Promise<void> {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message_id: messageId, rating }),
  });
  if (!res.ok) throw new Error("Feedback failed");
}
