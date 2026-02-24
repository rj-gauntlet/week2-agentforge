# LangSmith observability

LangSmith gives you traces for every agent run: input → LLM reasoning → tool calls → output, plus latency and token usage.

## Setup (one-time)

1. **Create an account** at [smith.langchain.com](https://smith.langchain.com) (free tier available).
2. **Get an API key:** Settings → API Keys → Create.
3. **Add to `.env`** (or your deployment environment):
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

## What you get

- **Traces:** Each `run_agent()` call appears as a run. Expand to see the chain: user message → model → tool calls (with inputs/outputs) → final reply.
- **Latency:** Per-step and total duration.
- **Token usage:** Input/output tokens per LLM call (and cost if the UI supports it).
- **Errors:** Failed tool calls or model errors with context.

## Disabling traces

Set `LANGCHAIN_TRACING_V2=false` or remove `LANGCHAIN_API_KEY` to stop sending data to LangSmith.
