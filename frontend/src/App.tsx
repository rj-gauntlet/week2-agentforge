import * as React from "react";
const { useState, useRef, useEffect } = React;
import { sendMessage, sendFeedback, type ChatMessage as ApiMessage, type ToolUsed } from "./api";
import "./App.css";

interface MessageWithMeta {
  role: "user" | "assistant";
  content: string;
  turn?: number;
  tools?: ToolUsed[];
}

const PRESETS = [
  { label: "Rx Interaction Check", query: "Do aspirin and ibuprofen interact?" },
  { label: "Symptom Triage", query: "I have a headache and fever. What could it be?" },
  { label: "Find Provider", query: "Can you find me a cardiologist in Austin, TX?" },
  { label: "Check Schedule", query: "Any open slots for prov_001 next week?" },
  { label: "Verify Insurance", query: "Does plan plan_001 cover procedure 99213?" },
  { label: "Interpret Labs", query: "Can you interpret these labs? Glucose 115, HDL 35, Potassium 4.0" },
  { label: "Contraindication", query: "Can a patient with an active infection get a knee replacement?" },
];

/** Format assistant text for display: preserve newlines and break list-like lines (multiple " - ") into separate lines. */
function formatMessageText(text: string): string {
  return text
    .split("\n")
    .map((line) => {
      const parts = line.split(" - ");
      if (parts.length <= 2) return line;
      return parts.map((p, i) => (i === 0 ? p : `- ${p.trim()}`)).join("\n");
    })
    .join("\n");
}

function App() {
  const [messages, setMessages] = useState<MessageWithMeta[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feedbackSent, setFeedbackSent] = useState<Set<number>>(new Set());
  const [presetQuery, setPresetQuery] = useState<string | null>(null);
  const [showToolsUsed, setShowToolsUsed] = useState(true);
  const [showUserFeedback, setShowUserFeedback] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const turnRef = useRef(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const text = (presetQuery ?? input).trim();
    if (!text || loading) return;

    setInput("");
    setPresetQuery(null);
    setError(null);
    turnRef.current += 1;
    const turn = turnRef.current;

    const history: ApiMessage[] = messages.map((m) => ({ role: m.role, content: m.content }));

    setMessages((prev) => [...prev, { role: "user", content: text, turn }]);
    setLoading(true);

    try {
      const res = await sendMessage(text, history);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.output,
          turn,
          tools: res.tools_used?.length ? res.tools_used : undefined,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, something went wrong. Please try again.", turn },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (turn: number, rating: "thumbs_up" | "thumbs_down") => {
    try {
      await sendFeedback(`turn_${turn}`, rating);
      setFeedbackSent((prev) => new Set(prev).add(turn));
    } catch {
      // toast or inline message optional
    }
  };

  const effectiveInput = presetQuery ?? input;

  return (
    <div className={`app ${isSidebarOpen ? "" : "sidebar-closed"}`}>
      <aside className="sidebar">
        <div className="sidebar-header-row">
          <h3><span className="sidebar-logo-icon">⚕️</span> AgentForge Clinical</h3>
          <button 
            className="sidebar-toggle" 
            onClick={() => setIsSidebarOpen(false)}
            aria-label="Collapse sidebar"
            title="Collapse sidebar"
          >
            ◀
          </button>
        </div>
        <p className="subtitle">Your intelligent healthcare assistant.</p>
        <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "0.75rem" }}>
          Click to instantly send a query:
        </p>
        {PRESETS.map((p) => (
          <button key={p.query} type="button" onClick={() => setPresetQuery(p.query)}>
            {p.label}
          </button>
        ))}
        <details className="sidebar-settings">
          <summary>Settings</summary>
          <div className="settings-panel">
            <label>
              <input
                type="checkbox"
                checked={showToolsUsed}
                onChange={(e) => setShowToolsUsed(e.target.checked)}
              />
              Show tools used
            </label>
            <label>
              <input
                type="checkbox"
                checked={showUserFeedback}
                onChange={(e) => setShowUserFeedback(e.target.checked)}
              />
              Show user feedback
            </label>
          </div>
        </details>
        <div className="hipaa">
          ⚠️ <strong>Notice:</strong> All queries are logged for HIPAA compliance. Do not enter PHI.
        </div>
      </aside>

      <main className="main">
        {!isSidebarOpen && (
          <button 
            className="sidebar-toggle-open" 
            onClick={() => setIsSidebarOpen(true)}
            aria-label="Expand sidebar"
            title="Expand sidebar"
          >
            ▶
          </button>
        )}
        <header className="header">
          <h1 className="title">
            <span>+</span>
            <span>AGENTFORGE AI ASSISTANT</span>
          </h1>
          <p className="subtitle">
            Ask me to check drug interactions, look up symptoms, find providers, or check insurance.
          </p>
        </header>

        <div className="whatsapp-notice">
          <p>
            <strong>Note:</strong> You can also interact with AgentForge via WhatsApp! Text us at <strong>+1 (415) 523-8886</strong> with the code <strong>join soon-vowel</strong> to connect.
          </p>
        </div>

        <div className="messages">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              <div className="bubble">
                <div className="message-text">{msg.role === "assistant" ? formatMessageText(msg.content) : msg.content}</div>
                {msg.role === "assistant" && showToolsUsed && msg.tools && msg.tools.length > 0 && (
                  <details className="tools-expander">
                    <summary>TOOLS USED: {[...new Set(msg.tools.map((t) => t.name))].join(", ")}</summary>
                    {msg.tools.map((t, j) => (
                      <div key={j} className="tool-block">
                        <strong>{t.name}</strong>
                        <div>Inputs</div>
                        <pre>{JSON.stringify(t.args, null, 2)}</pre>
                        {t.output != null && (
                          <span style={{ display: "contents" }}>
                            <div>Outputs</div>
                            <pre>
                              {typeof t.output === "object"
                                ? JSON.stringify(t.output, null, 2)
                                : String(t.output)}
                            </pre>
                          </span>
                        )}
                      </div>
                    ))}
                  </details>
                )}
                {msg.role === "assistant" && showUserFeedback && msg.turn != null && (
                  <div className="feedback-row">
                    {feedbackSent.has(msg.turn) ? (
                      <p className="feedback-caption">Thanks for your feedback!</p>
                    ) : (
                      <span style={{ display: "contents" }}>
                        <p className="feedback-caption">Was this helpful?</p>
                        <button type="button" className="feedback-btn feedback-btn-yes" onClick={() => handleFeedback(msg.turn!, "thumbs_up")} aria-label="Yes, helpful">
                          <span aria-hidden>✓</span>
                        </button>
                        <button type="button" className="feedback-btn feedback-btn-no" onClick={() => handleFeedback(msg.turn!, "thumbs_down")} aria-label="No, not helpful">
                          <span aria-hidden>✗</span>
                        </button>
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && <p className="spinner">QUERYING DATABASE...</p>}
          {error && <p className="error">{error}</p>}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <form onSubmit={handleSubmit}>
            <input
              type="text"
              value={effectiveInput}
              onChange={(e) => (presetQuery ? setPresetQuery(e.target.value) : setInput(e.target.value))}
              placeholder="Type your clinical query here..."
              disabled={loading}
              aria-label="Clinical query"
            />
            <button type="submit" disabled={loading || !effectiveInput.trim()}>
              Send
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}

export default App;
