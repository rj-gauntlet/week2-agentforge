# AgentForge — Agent Architecture Document

**Version:** 1.0 (Final Submission)  
**Purpose:** Domain, architecture, verification, eval results, observability, and open source plan for submission and future maintenance.  
**Reference:** [PRD.md](../PRD.md), [PRE_SEARCH.md](../PRE_SEARCH.md), [ROADMAP.md](../ROADMAP.md).

---

## 1. Domain & Use Cases

**Domain:** Healthcare (OpenEMR-aligned). The agent is a clinical/admin assistant for a practice setting, not a diagnostic or prescribing system.

**Problems solved:**

- **Drug interaction checks** — “Do aspirin and ibuprofen interact?” → severity and guidance; no dosing.
- **Symptom lookup** — Possible conditions and urgency only; never diagnoses; always “consult your provider.”
- **Provider search** — By specialty and location (e.g. pediatrician in Austin, TX).
- **Appointment availability** — Slots for a provider in a date range (14-day rolling window; mock for sprint).
- **Insurance coverage** — Procedure code + plan ID → covered or not, details.
- **Procedure lookup** — CPT code by name or name by code.
- **Lab result interpretation** — User-provided values (e.g. glucose, HDL) checked against reference ranges; disclaimer required.
- **Contraindication check** — Procedure code + conditions/medications → safe or flagged issues.

**Scope boundaries:** No diagnosis, no dosing advice, no prescription. All clinical-style answers cite tools and include a provider-consult disclaimer where appropriate. Out-of-domain or adversarial requests are refused.

---

## 2. Agent Architecture

**Framework:** LangChain. Single agent with tool-calling and in-memory conversation history.

**Flow:**

1. User message (and optional chat history) → orchestrator.
2. Input verification (domain check, PHI redaction) before the LLM.
3. Messages (system + history + user) → LangChain agent `invoke()`; model chooses tools and arguments.
4. Tool executions return structured JSON; agent may chain multiple tools (e.g. procedure_lookup → insurance_coverage_check).
5. Final assistant message extracted; then output verification (safety disclaimer, fact-check vs tool output).
6. Token usage extracted from AIMessages and logged for cost analysis.

**Components:**

| Component | Implementation |
|-----------|----------------|
| **Reasoning engine** | LLM (OpenAI GPT-4o or Anthropic Claude Sonnet) via LangChain; temperature 0. |
| **Tool registry** | Eight tools in `agent/tools/`: drug_interaction_check, symptom_lookup, provider_search, appointment_availability, insurance_coverage_check, procedure_lookup, lab_result_interpretation, contraindication_check. Each has schema + description; wrappers in `langchain_tools.py` return JSON strings from shared `tool_result(success, data?, error?)`. |
| **Memory** | Conversation history passed per request (list of `{role, content}`); no persistent user store. |
| **Orchestrator** | `agent/orchestrator.py`: `run_agent(query, chat_history, source)` builds agent, runs invoke, runs verification, logs cost, returns output + messages + usage. |
| **Verification layer** | See §3. |
| **Cost tracking** | `agent/cost_logging.py`: extracts usage from AIMessage `usage_metadata` (or `response_metadata`), estimates USD, appends to `data/cost_log.jsonl` with `source` (api | eval). |

**Tool data sources:** The `drug_interaction_check` tool connects to the live **OpenFDA API** to fetch real-world interaction data. Procedures, providers, coverage, symptoms, and contraindications are mock/static JSON data, while appointments use a dynamic 14-day rolling window generator. Production path: replace the remaining static datasets with OpenEMR FHIR, scheduling, and billing APIs where applicable.

---

## 3. Verification Strategy

Four types are implemented and used on every request where applicable:

| # | Type | What it does |
|---|------|----------------|
| 1 | **Domain constraints / input validation** | Heuristic check for adversarial phrases (“ignore previous”, “system prompt”, “hack”, “talk like a pirate”); short-circuits with refusal before LLM. |
| 2 | **Output safety / disclaimer** | If output contains clinical keywords (e.g. headache, fever, symptom, diagnose) but no “not a diagnosis” / “consult your provider”, appends a standard disclaimer. |
| 3 | **PHI redaction** | Redacts SSN, phone numbers, and DOB-like patterns in user input before sending to the LLM. |
| 4 | **Fact-check vs tool output** | If drug_interaction_check was used and tool said “minor”, but the model’s reply says “fatal” or “major”, appends a fact-check warning. |

Persona lock is enforced in the system prompt: no adopting other personas or styles. Lab interpretation is explicitly instructed to use the tool and add the consult-provider disclaimer.

---

## 4. Eval Results

**Harness:** `scripts/run_eval_harness.py` loads `data/eval_cases.json`, runs each case through `run_agent(..., source="eval")`, and checks expected tools, output phrases (OR), optional flags, and optional `expected_tool_output` (e.g. `appointment_availability.available`, `contraindication_check.safe`). Results written to `data/eval_results_latest.json` and a timestamped copy under `data/eval_results/`.

**Dataset:** 56 test cases.

| Category | Count | Pass rate (latest) |
|----------|--------|---------------------|
| Happy path | 25 | 100% |
| Multi-step | 11 | 100% |
| Edge case | 10 | 100% |
| Adversarial | 10 | 100% |
| **Overall** | **56** | **100%** |

**Criteria:** Correct tool(s) invoked; at least one of `expected_output_contains` in reply; optional `expected_flags` (e.g. no-diagnosis) and `expected_tool_output` (structured tool fields) satisfied. Failures are recorded in the results JSON for regression and analysis.

**Failure Analysis & Iteration:** Early iterations revealed minor failures in multi-step date tracking for appointment availability, which we resolved by enforcing an `available` boolean inside the tool’s structured JSON to give the LLM unambiguous availability data. We also fortified the system prompt to explicitly restrict out-of-domain conversational requests and refuse role-playing jailbreaks (e.g., “talk like a pirate” or “hack a database”), resulting in a 100% pass rate.

**Reference:** [EVAL.md](../EVAL.md) for dataset format and how to run.

---

## 5. Observability Setup

**LangSmith:** With `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` in `.env`, every `run_agent()` produces a trace: input → model → tool calls (inputs/outputs) → final reply. Dashboard shows latency, token usage, and errors. See [LANGSMITH.md](../LANGSMITH.md).

**Cost log:** Each API and eval run that uses the LLM appends a line to `data/cost_log.jsonl`: timestamp, source (api | eval), model_hint, input_tokens, output_tokens, total_tokens, estimated_usd, query_preview. Pricing assumptions (e.g. $2.50/$10 per 1M for GPT-4o, $3/$15 for Claude) are in `agent/cost_logging.py` and can be updated for AI Cost Analysis and production projections.

**Feedback:** Frontend thumbs up/down call `POST /feedback`; can be wired to observability or analytics for iteration.

---

## 6. Open Source Contribution

**Released:** We have released our comprehensive **AgentForge Healthcare Eval Dataset** directly within the open source repository. 
- **Location:** `data/eval_cases.json` (56 diverse, verified test cases including happy path, edge cases, and adversarial prompt injections).
- **Format & Running:** Instructions for using the included test harness are documented in [EVAL.md](../EVAL.md).
- **Purpose:** This contribution allows other developers building clinical, EMR, or healthcare AI assistants to benchmark their agent’s tool-calling reliability, safety guardrails, and compliance limits against a robust baseline. 
- **License:** MIT License for the dataset, matching the open source intent of the project.

---

*This document serves as the final Agent Architecture deliverable.*
