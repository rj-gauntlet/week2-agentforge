# LangSmith observability

LangSmith gives you traces for every agent run: input → LLM reasoning → tool calls → output, plus latency and token usage.

## Setup (one-time)

1. **Create an account** at [smith.langchain.com](https://smith.langchain.com) (free tier available).
2. **Get an API key:** Settings → API Keys → Create.
3. **Add to `.env`** (for local dev and when you run the eval harness):
   ```env
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=lsv2_pt_xxxxxxxx
   LANGCHAIN_PROJECT=agentforge-mvp
   ```
4. **Install deps** (already in `requirements.txt`):
   ```powershell
   .\.venv\Scripts\pip.exe install -r requirements.txt
   ```

No code changes are required. LangChain automatically sends traces when these variables are set.

### UI / production: traces from the deployed app

Traces for **UI chat requests** are sent by the process that handles the request—the **backend**. If your frontend talks to a backend on Railway (or another host), that backend must have the same LangSmith env vars set, or UI traffic will not appear in LangSmith.

- In **Railway**: open your **backend** service → **Variables** → add `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_API_KEY=your_key`, and optionally `LANGCHAIN_PROJECT=agentforge-mvp`.
- Redeploy the backend so the new variables are picked up.

After that, requests from the web UI will show up in LangSmith under **Tracing** like your local eval runs.

## What you get

- **Traces:** Each `run_agent()` call appears as a run. Expand to see the chain: user message → model → tool calls (with inputs/outputs) → final reply.
- **Latency:** Per-step and total duration.
- **Token usage:** Input/output tokens per LLM call (and cost if the UI supports it).
- **Errors:** Failed tool calls or model errors with context.

## Evals: Traces vs Datasets & Experiments

- **`scripts/run_eval_harness.py`** — Custom harness: runs each case through the agent and writes pass/fail to `data/eval_results_latest.json`. It just calls `run_agent()` in a loop, so each run is sent to LangSmith as a **Trace**. You see them under **Tracing**, not under **Datasets** or **Experiments**.

- **`scripts/run_evals.py`** — LangSmith-native evals: creates a **Dataset** from `data/eval_cases.json`, runs the agent on each example via LangSmith’s `evaluate()`, and records an **Experiment**. Use this when you want evals to show up under **Datasets** and **Experiments** in the LangSmith UI.

  From project root (with `LANGCHAIN_API_KEY` set):
  ```powershell
  .\.venv\Scripts\python.exe scripts\run_evals.py
  ```
  The script creates/updates the dataset "AgentForge Healthcare Evals", runs the experiment, and you can view results and compare runs under **Experiments**.

## Disabling traces

Set `LANGCHAIN_TRACING_V2=false` or remove `LANGCHAIN_API_KEY` to stop sending data to LangSmith.
