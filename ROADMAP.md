# AgentForge — One-Week Roadmap

**Timeline:** 7 days to Final (Sunday 10:59 PM CT)  
**Reference:** [PRD.md](./PRD.md) for requirements and decision rules.

---

## Overview

| Phase | Deadline | Focus |
|-------|----------|--------|
| **Pre-Search** | 2 hours | Architecture, stack, plan — no code yet |
| **MVP** | 24 hours (Tuesday) | Basic agent, 3+ tools, deployed, 5+ evals |
| **Early submission** | Friday (Day 4) | Eval framework + observability in place |
| **Final** | Sunday (Day 7) | Production-ready + open source + all deliverables |

---

## Day 0 — Pre-Search (First 2 Hours) ✅

**Goal:** Complete Pre-Search checklist; lock domain, framework, and observability. No code.

**Deliverable:** [PRE_SEARCH.md](./PRE_SEARCH.md) — full checklist + Constraints & Assumptions.

### Hour 1 — Phase 1: Define Constraints

- [x] **Domain:** Choose Healthcare (OpenEMR) or Finance (Ghostfolio). Document use cases and verification needs.
- [x] **Scale & performance:** Query volume, latency (<5s single-tool, <15s multi-step), cost limits.
- [x] **Reliability:** Cost of wrong answers; non-negotiable verification; human-in-the-loop if any.
- [x] **Team/skills:** Framework familiarity, domain experience, eval/observability comfort.

**Output:** 1–2 page “Constraints & assumptions” (can be in Pre-Search doc).

### Hour 2 — Phases 2 & 3: Architecture & Refinement

- [x] **Framework:** LangChain vs LangGraph vs other — decide and document why.
- [x] **LLM:** GPT-5 / Claude / open source — function calling, context, cost.
- [x] **Tools:** List 5+ tools for chosen domain; map to forked repo where possible.
- [x] **Observability:** LangSmith vs Braintrust vs other — decide and note setup steps.
- [x] **Eval approach:** LangSmith Evals, Braintrust, or custom; ground truth strategy.
- [x] **Verification:** Pick 3+ verification types; data sources and thresholds.
- [x] **Failure modes:** Tool failures, ambiguous queries, rate limits, fallbacks.
- [x] **Open source:** Choose contribution type (package, dataset, PR, tool, docs).

**Output:** Pre-Search document is [PRE_SEARCH.md](./PRE_SEARCH.md). **Your actions:** (1) Confirm domain (Finance/Ghostfolio recommended). (2) Fork and clone [Ghostfolio](https://github.com/ghostfolio/ghostfolio) (or OpenEMR). (3) Save this AI conversation for the Pre-Search deliverable.

---

## Day 1 — MVP (By 24-Hour Mark / Tuesday)

**Goal:** All MVP requirements met; agent deployed and publicly accessible.

### Morning — Basic agent + one tool

- [x] **Repo:** Fork chosen repo (if not done); create `agent` or `api` area for agent code.
- [x] **Stack:** Init backend (e.g. Python/FastAPI or Node/Express); add agent framework and LLM client.
- [x] **Tool registry:** Define first tool (schema + description + execution). Pick highest-value, simplest tool (e.g. `drug_interaction_check` or `portfolio_analysis`).
- [x] **Orchestrator:** Single agent flow: user message → LLM → optional tool call → response.
- [x] **End-to-end:** One natural language query → one tool call → structured result → coherent reply. No crashes.

### Afternoon — Expand tools + memory + errors

- [x] **Tools 2 & 3 (minimum 3):** Add two more tools; same pattern (schema, execute, structured return). Verify each in isolation.
- [x] **Conversation history:** Persist or pass conversation context across turns (memory component).
- [x] **Error handling:** Try/except around tool execution and LLM calls; graceful messages; no uncaught exceptions.
- [x] **Verification (≥1):** One domain-specific check (e.g. fact check, constraint, or “no medical advice” guardrail).

### Evening — Eval + deploy

- [x] **Simple evaluation:** 5+ test cases with expected outcomes (input, expected tool call/result, pass/fail). Run and record results.
- [x] **Deploy:** Deploy to Vercel / Railway / Modal / cloud. Public URL.
- [x] **Smoke test:** Run MVP checklist from PRD against deployed app.

**MVP gate checklist (all required):**  
☑ Natural language in domain ☑ ≥3 tools ☑ Structured tool results ☑ Synthesis of results ☑ Conversation history ☑ Basic error handling ☑ ≥1 verification ☑ 5+ test cases ☑ Deployed & public

---

## Day 2 — Tools 4–5 + Multi-Step + Observability Start

**Goal:** All 5 tools; multi-step reasoning; observability integrated.

### Morning

- [x] **Tools 4 & 5:** Implement remaining two tools; test individually.
- [x] **Multi-step:** Ensure orchestrator can chain 2–3 tools when needed (e.g. search → filter → return). Add 2–3 test scenarios.

### Afternoon

- [x] **Observability:** Integrate LangSmith: trace logging (input → reasoning → tool calls → output). Set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY`; see [LANGSMITH.md](./LANGSMITH.md).
- [x] **Latency / Token usage / Errors:** LangSmith dashboard shows per-step latency, token usage, and errors with context.

### Evening

- [x] **Smoke test:** Run 5+ evals with tracing on; confirm traces appear in LangSmith.

---

## Day 3 — Eval Framework + Dataset Growth

**Goal:** Eval framework in place; dataset growing toward 50 cases.

### Morning

- [x] **Eval harness:** Automated runner for test cases (input, expected tool calls/output, pass/fail). Integrate with observability if supported (e.g. LangSmith Evals).
- [x] **Happy path:** Add happy-path cases toward 20+ total (can include original 5).
- [x] **Edge cases:** Add 5+ edge cases (missing data, boundaries, invalid input).

### Afternoon

- [x] **Adversarial:** Add 5+ adversarial cases (prompt injection, bypass verification, harmful requests).
- [x] **Multi-step:** Add 5+ multi-step reasoning scenarios (expected tool chain + output).
- [x] **Baseline run:** Full eval run; record pass rate by category. Target >80% overall later.

### Evening

- [x] **Regression:** Ensure eval results are stored/historical (for “Eval results” in observability).
- [x] **Document:** Eval dataset format and how to run (for submission and open source).

---

## Day 4 — Early Submission (Friday): Eval + Observability Solid

**Goal:** Eval framework complete; observability fully usable. Early submission bar met.

### Morning

- [ ] **50 test cases:** Reach 20+ happy, 10+ edge, 10+ adversarial, 10+ multi-step. Document each with expected outcomes and criteria.
- [ ] **Eval results dashboard/report:** Historical scores; ability to detect regressions (via observability or script).

### Afternoon

- [ ] **Observability complete:** Trace, latency, errors, token usage, eval results, plus mechanism for user feedback (e.g. thumbs up/down endpoint or UI).
- [ ] **Verification (3+):** Implement two more verification types (e.g. fact checking, confidence scoring, domain constraints, output validation, or human-in-the-loop trigger). Document in architecture notes.

### Evening

- [ ] **Run full eval suite:** Record pass rate; fix critical failures if time allows.
- [ ] **Early submission checkpoint:** Confirm eval framework + observability are done and documented.

---

## Day 5 — Verification + Performance + Iteration

**Goal:** All verifications in place; performance near targets; evals driving fixes.

### Morning

- [ ] **Verification polish:** Ensure 3+ verification types are wired and tested. Document in Agent Architecture Doc draft.
- [ ] **Performance:** Measure latency (single-tool <5s, multi-step <15s); tool success rate; address bottlenecks.

### Afternoon

- [ ] **Eval iteration:** Fix failures from Day 4 run; improve tool selection and error handling. Re-run suite.
- [ ] **Safety & consistency:** Add or tighten tests for safety and consistency; target >80% eval pass rate.

### Evening

- [ ] **Cost tracking:** Start logging actual dev/test token usage and API costs for AI Cost Analysis.
- [ ] **Agent Architecture Doc:** First full draft (domain, architecture, verification, eval results, observability, open source plan).

---

## Day 6 — Open Source + Docs + Cost Analysis

**Goal:** Open source contribution done or in final form; docs and cost analysis ready.

### Morning

- [ ] **Open source:** Complete chosen contribution — publish package / release dataset / open PR / publish tool / publish tutorial. Get link.

### Afternoon

- [ ] **AI Cost Analysis:** Dev spend (tokens, calls, observability). Production table for 100 / 1K / 10K / 100K users with assumptions (queries per user, tokens, tool calls, verification).
- [ ] **Agent Architecture Doc:** Finalize 1–2 pages (all sections from PRD template).
- [ ] **README / setup guide:** Repo README with setup, architecture overview, deployed link.

### Evening

- [ ] **Pre-Search doc:** Ensure Pre-Search checklist (Phases 1–3) is saved and referenced in submission.
- [ ] **Final eval run:** 50+ cases with results; save as deliverable (and for open source if releasing dataset).

---

## Day 7 — Final (Sunday, By 10:59 PM CT)

**Goal:** All deliverables submitted; demo video and social post done.

### Morning

- [ ] **Deployed app:** Verify public URL; smoke test and one full user flow.
- [ ] **Demo video (3–5 min):** Agent in action, eval results, observability dashboard. Upload and link in submission.
- [ ] **Submission checklist:** GitHub repo, demo video link, Pre-Search doc, Agent Architecture Doc, AI Cost Analysis, Eval dataset (50+ with results), Open source link, deployed URL.

### Afternoon

- [ ] **Social post:** X or LinkedIn — description, features, demo/screenshots, tag @GauntletAI.
- [ ] **Last pass:** Performance targets, verification accuracy, hallucination rate — document in architecture doc or cost analysis where relevant.

### Before 10:59 PM CT

- [ ] **Submit:** All links and files per course instructions.
- [ ] **Interview prep:** Review PRD “Interview Prep”; rehearse framework choice, tool design, verification, evals, scaling.

---

## Quick Reference — Priority Order (From PRD)

1. Basic agent (one tool end-to-end)  
2. Tool expansion (3 → 5 tools)  
3. Multi-step reasoning  
4. Observability  
5. Eval framework + baseline  
6. Verification layer (3+ types)  
7. Iterate on evals  
8. Open source prep and release  

---

## Risk Mitigation

| Risk | Mitigation |
|------|-------------|
| MVP late | Do not add extra features before 3 tools + deploy. Cut scope, not quality. |
| Eval bottleneck | Start eval harness and 5 cases on Day 1; add cases daily. |
| Observability delay | Integrate on Day 2; use default dashboard, no custom UI required. |
| Open source scope creep | Pick one contribution type in Pre-Search; stick to it. |
| Deployment issues | Deploy early (Day 1); use known stack (e.g. Railway, Vercel). |

---

## Daily Time Budget (Suggested)

- **Pre-Search:** 2 hours (Day 0).  
- **Days 1–4:** 8–10 hours/day (MVP and Early Submission).  
- **Days 5–7:** 6–8 hours/day (polish, docs, video, submission).  

Adjust based on your schedule; keep MVP and deploy on Day 1 as the non-negotiable anchor.
