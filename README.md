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

**Eval dataset:** [data/eval_cases.json](./data/eval_cases.json) — cases by category (happy_path, edge_case, adversarial, multi_step).  
**Eval harness:** [scripts/run_eval_harness.py](./scripts/run_eval_harness.py) — automated runner; writes pass/fail to [data/eval_results_latest.json](./data/eval_results_latest.json) and a timestamped copy under `data/eval_results/` for history.  
**Full eval guide:** [EVAL.md](./EVAL.md) — dataset format, how to run, and observability.

**To run the eval harness (full dataset, recommended):**
1. Ensure your `.env` has `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`.
2. From the project root:
   ```powershell
   .\.venv\Scripts\python.exe scripts\run_eval_harness.py
   ```
3. View per-category and overall pass rate in the terminal; results are saved to `data/eval_results_latest.json` for regression tracking.
4. Optional: set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` in `.env` to send traces to LangSmith.

**To run evals via pytest (including MVP smoke tests):**
```powershell
.\.venv\Scripts\python.exe -m pytest tests/eval -v
```
(Skips tests that require an API key if none is set.)

**Eval dataset format** (`data/eval_cases.json`): each case is an object with `category`, `query`, `expected_tools`, `expected_output_contains`, and optional:
- `expected_flags` (e.g. `{"can_diagnose": false}` to require a consult-provider disclaimer)
- `expected_tool_output` — structured assertions on tool return values (e.g. `{"insurance_coverage_check": {"covered": false}}`) so evals don't depend on exact wording. The harness checks that the named tool's returned JSON includes the given key-value pairs.

---

## Open Source Contribution: Healthcare Agent Eval Dataset

As our Open Source contribution to the broader agentic healthcare community, we have released our comprehensive **AgentForge Healthcare Eval Dataset** directly within this repository. 

- **What:** 56 highly-curated, structured test cases representing real-world clinical and administrative queries (e.g. drug interactions, contraindications, procedure lookup). 
- **Where:** [`data/eval_cases.json`](./data/eval_cases.json)
- **Why:** To give developers building healthcare AI assistants a robust baseline to benchmark tool-calling reliability, multi-step reasoning, and strict safety guardrails (including adversarial/jailbreak attempts).
- **Use it:** The dataset is fully usable via our included eval harness. See [EVAL.md](./EVAL.md) for full documentation on the dataset schema and how to integrate it into your own testing pipelines.
- **License:** Released under the MIT License.

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
