# Project Status vs Goals & Timeline

**As of:** Current session.  
**Reference:** [PRD.md](./PRD.md), [ROADMAP.md](./ROADMAP.md).

---

## PRD MVP Requirements (9 required)

| # | Requirement | Status | Notes |
|---|-------------|--------|--------|
| 1 | Natural language in domain | ✅ Done | Agent responds to healthcare queries via orchestrator + tools. |
| 2 | ≥3 functional tools | ✅ Done | 5 tools: drug_interaction_check, provider_search, appointment_availability, symptom_lookup, insurance_coverage_check. |
| 3 | Structured tool results | ✅ Done | All tools return `{ success, data?, error? }` via `tool_result()`. |
| 4 | Agent synthesizes results | ✅ Done | Orchestrator returns coherent text; system prompt asks to cite tools. |
| 5 | Conversation history | ✅ Done | `run_agent(query, chat_history=...)` and POST /chat accept `history`. |
| 6 | Basic error handling | ✅ Done | try/except in `run_agent`; API returns 500 with detail on failure. |
| 7 | ≥1 verification | ✅ Done | System prompt: no diagnosis, “consult your provider,” cite tool. |
| 8 | 5+ test cases | ✅ Done | 5 eval cases + unit/integration; all 32 tests pass. |
| 9 | **Deployed and publicly accessible** | ❌ **Not done** | App runs locally only; no public URL yet. |

**MVP gap:** **Deploy** to Railway / Render / Modal / etc. and get a **public URL**, then run a smoke test against it.

---

## ROADMAP alignment

### Day 0 — Pre-Search ✅

- PRE_SEARCH.md done; domain Healthcare (OpenEMR); LangChain; tools and observability decided.

### Day 1 — MVP (mostly done)

- **Done:** Stack (Python/FastAPI), 5 tools, orchestrator, conversation history, error handling, verification (prompt), 5+ evals, local API.
- **Not done:** Deploy to cloud, public URL, smoke test on deployed app.
- **Note:** Repo is standalone (week2-agentforge); PRD also mentions forking OpenEMR. If the gate requires a fork, you’d add this agent as a feature in an OpenEMR fork; otherwise the current repo may satisfy “agent with tool use.”

### Day 2+ — Not started

- **Day 2:** Multi-step tool chaining (orchestrator can already use multiple tools in one turn), observability (LangSmith etc.), latency/token logging.
- **Day 3–4:** Eval framework growth to 50+ cases, adversarial/edge cases, observability dashboard, 3+ verification types.
- **Day 5–7:** Verification polish, performance targets, open source contribution, Agent Architecture Doc, AI Cost Analysis, demo video, submission.

---

## Suggested next steps (in order)

1. **Deploy** — Get the FastAPI app on Railway, Render, or Modal with a public URL; set `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`) in the platform’s env.
2. **Smoke test** — Hit the deployed `/health` and `/chat` once; confirm MVP checklist against the live URL.
3. **Day 2** — Add observability (e.g. LangSmith), then expand evals and verification per ROADMAP.
