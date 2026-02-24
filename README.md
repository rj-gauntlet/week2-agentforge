# AgentForge — Healthcare Agent

Production-style healthcare AI agent for clinical/admin use: drug interactions, symptom lookup, provider search, appointment availability, insurance coverage. Built with LangChain and FastAPI.

See [PRD.md](./PRD.md), [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md), and [ROADMAP.md](./ROADMAP.md) for goals and timeline.

---

## Setup

From the project root (no activation — use the venv’s Python/pip by path):

```powershell
cd c:\Users\rjxxl\projects\week2-agentforge
python -m venv .venv
.\.venv\Scripts\pip.exe install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`.

---

## Run the API locally

From the project folder (no activation). If you’re already in `week2-agentforge`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

If port 8000 is in use (e.g. “only one usage of each socket address”), use another port: `--port 8001` (then open http://localhost:8001/health).

If you need to change directory first: `cd c:\Users\rjxxl\projects\week2-agentforge` then run the line above.

- **Deploy:** See **[DEPLOY.md](DEPLOY.md)**. Live API: **https://web-production-0f3ae.up.railway.app** (health: `/health`, chat: `POST /chat`).

- **Health:** `GET http://localhost:8000/health`
- **Chat:** `POST http://localhost:8000/chat` with JSON body:
  - `message` (required): user message
  - `history` (optional): list of `{ "role": "user"|"assistant", "content": "..." }` for conversation context

Example:

```bash
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"Do aspirin and ibuprofen interact?\"}"
```

---

## Testing

From the project folder (no activation):

```powershell
# Run Unit Tests
.\.venv\Scripts\python.exe -m pytest tests/unit -v

# Run Evaluation Tests (Evals)
.\.venv\Scripts\python.exe -m pytest tests/eval -v
```

See [TESTING.md](./TESTING.md) for TDD and detailed instructions.

---

## Evaluation Tests (Evals)

Per the MVP requirements, this project includes a robust suite of end-to-end evaluation tests that verify the agent's ability to reason, call tools, and handle multi-step chains.

**👉 Link to Evals File:** [tests/eval/test_eval_mvp.py](./tests/eval/test_eval_mvp.py)

**To run the evals for your demonstration video:**
1. Ensure your `.env` is configured with a valid API key.
2. Run the following command from the project root:
   ```powershell
   .\.venv\Scripts\python.exe -m pytest tests/eval/test_eval_mvp.py -v
   ```
3. Watch the terminal output as the agent successfully parses medical queries, triggers the correct underlying tools (e.g., `drug_interaction_check`, `provider_search`), and synthesizes a safe response.

---

## Deployment

Deploy the FastAPI app so it is **publicly accessible** (MVP requirement). Options:

- **Railway:** Connect repo, set root directory to project root, add `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`) in Variables. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
- **Modal:** Run the app as a Modal web endpoint; set env secrets for the LLM key.
- **Vercel / other:** Run `uvicorn main:app --host 0.0.0.0 --port 8000` in a Python runtime; expose port 8000 and set the API key in the environment.

After deployment, use the public URL for `/health` and `/chat` (e.g. `POST https://your-app.up.railway.app/chat`).

---

## Architecture

- **Agent:** [agent/orchestrator.py](agent/orchestrator.py) — LangChain agent with tool-calling and conversation memory.
- **Tools:** [agent/tools/](agent/tools/) — `drug_interaction_check` (real data), `provider_search`, `appointment_availability`, `symptom_lookup`, `insurance_coverage_check` (mocks).
- **API:** [main.py](main.py) — FastAPI app exposing `/health` and `/chat`.
