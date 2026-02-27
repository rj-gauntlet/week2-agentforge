# AgentForge — Product Requirements Document (PRD)

**Version:** 1.0  
**Scope:** One-week sprint — Production-ready domain-specific AI agents  
**Gate:** Project completion + interviews required for Austin admission.

---

## 1. Project Summary

| Item | Value |
|------|--------|
| **Goal** | Build production-ready domain-specific AI agents on a forked open source project, with evaluation, verification, and observability. |
| **Domain options** | **Healthcare** (OpenEMR) **or** **Finance** (Ghostfolio) — choose ONE. |
| **Outcome** | Deployed agent + eval framework + observability + open source contribution + documentation. |

**Principle:** A reliable agent with solid evals and verification beats a flashy agent that hallucinates in production.

---

## 2. Deadlines (Hard Gates)

| Checkpoint | When | Focus |
|------------|------|--------|
| **Pre-Search** | 2 hours after receiving project | Architecture, plan, stack decisions |
| **MVP** | 24 hours (Tuesday) | Basic agent with tool use — **hard gate, all items required** |
| **Early Submission** | 4 days (Friday) | Eval framework + observability |
| **Final** | 7 days (Sunday 10:59 PM CT) | Production-ready + open source + all deliverables |

---

## 3. Domain & Repository

- **Choose ONE:** Healthcare (OpenEMR) or Finance (Ghostfolio).
- **Fork** the chosen repo; the agent must add **new meaningful features** in that fork.
- **Repos:**  
  - Healthcare: [OpenEMR](https://github.com/openemr/openemr)  
  - Finance: [Ghostfolio](https://github.com/ghostfolio/ghostfolio)

**PRD decision rule:** Domain choice drives tool design, verification rules, and eval scenarios. Lock domain in Pre-Search and document in Agent Architecture Doc.

---

## 4. MVP Requirements (24 Hours — All Required)

| # | Requirement | Pass criteria |
|---|-------------|----------------|
| 1 | Agent responds to natural language in chosen domain | User query → agent reply in domain context |
| 2 | **≥3 functional tools** agent can invoke | Tools defined with schemas and execution logic |
| 3 | Tool calls execute and return **structured results** | No silent failures; structured payloads |
| 4 | Agent **synthesizes** tool results into coherent responses | Multi-tool answers are summarized, not raw dumps |
| 5 | **Conversation history** across turns | Context/history maintained |
| 6 | **Basic error handling** | Graceful failure, no crashes |
| 7 | **≥1 domain-specific verification check** | e.g. fact check, constraint, or safety check |
| 8 | **Simple evaluation:** 5+ test cases with expected outcomes | Automated or scripted; pass/fail defined |
| 9 | **Deployed and publicly accessible** | URL works; no local-only runs for demo |

**PRD decision rule:** Prioritize one tool working end-to-end before adding more. “Simple agent with reliable tool execution beats a complex agent that hallucinates or fails unpredictably.”

---

## 5. Core Agent Architecture

### 5.1 Components (Required)

| Component | Requirement |
|-----------|-------------|
| **Reasoning engine** | LLM with structured output, chain-of-thought capability |
| **Tool registry** | Defined tools: schemas, descriptions, execution logic |
| **Memory** | Conversation history, context management, state persistence |
| **Orchestrator** | Decides when to use tools; handles multi-step reasoning |
| **Verification layer** | Domain-specific checks before returning responses |
| **Output formatter** | Structured responses with citations and confidence |

### 5.2 Required Tools (Minimum 5)

**Healthcare (examples — align with forked OpenEMR):**

- `drug_interaction_check(medications[])` → interactions, severity  
- `symptom_lookup(symptoms[])` → possible conditions, urgency  
- `provider_search(specialty, location)` → available providers  
- `appointment_availability(provider_id, date_range)` → slots  
- `insurance_coverage_check(procedure_code, plan_id)` → coverage details  

**Finance (examples — align with forked Ghostfolio):**

- `portfolio_analysis(account_id)` → holdings, allocation, performance  
- `transaction_categorize(transactions[])` → categories, patterns  
- `tax_estimate(income, deductions)` → estimated liability  
- `compliance_check(transaction, regulations[])` → violations, warnings  
- `market_data(symbols[], metrics[])` → current data  

**PRD decision rule:** Tools must be **domain-appropriate** and add value in the forked repo. Pre-Search should map repo capabilities to these (or adjusted) tools; document in architecture doc.

---

## 6. Evaluation Framework (Required)

### 6.1 Eval Dimensions

| Eval type | What to test |
|-----------|----------------|
| **Correctness** | Accurate information; fact-check vs ground truth |
| **Tool selection** | Right tool(s) for each query |
| **Tool execution** | Tool calls succeed; parameters correct |
| **Safety** | Refuses harmful requests; avoids hallucination |
| **Consistency** | Same input → same output where deterministic |
| **Edge cases** | Missing data, invalid input, ambiguous queries |
| **Latency** | Response time within acceptable bounds |

### 6.2 Eval Dataset (Minimum 50 Test Cases)

| Category | Minimum count | Notes |
|----------|----------------|--------|
| Happy path | 20+ | Expected outcomes defined |
| Edge cases | 10+ | Missing data, boundaries |
| Adversarial | 10+ | Attempts to bypass verification |
| Multi-step reasoning | 10+ | Chained tools, complex queries |

**Per test case:** input query, expected tool calls, expected output, pass/fail criteria.

**PRD decision rule:** Eval dataset is a deliverable; build incrementally as features are added. Pre-Search should decide: LangSmith Evals, Braintrust Evals, or custom.

---

## 7. Observability Requirements

| Capability | Requirement |
|------------|--------------|
| **Trace logging** | Full trace: input → reasoning → tool calls → output |
| **Latency tracking** | Time breakdown: LLM, tools, total response |
| **Error tracking** | Failures, stack traces, context; categorized |
| **Token usage** | Input/output tokens per request; cost tracking |
| **Eval results** | Historical scores; regression detection |
| **User feedback** | Thumbs up/down, corrections (mechanism only) |

**PRD decision rule:** Add observability early; needed to debug. Choose one: LangSmith, Braintrust, Langfuse, W&B, Arize Phoenix, Helicone, or custom. Document in Pre-Search and architecture doc.

---

## 8. Verification Systems (Implement 3+)

| Type | Implementation focus |
|------|----------------------|
| **Fact checking** | Cross-reference claims to authoritative sources |
| **Hallucination detection** | Flag unsupported claims; require source attribution |
| **Confidence scoring** | Quantify certainty; surface low-confidence |
| **Domain constraints** | Enforce rules (e.g. drug dosage limits) |
| **Output validation** | Schema validation, format, completeness |
| **Human-in-the-loop** | Escalation triggers for high-risk decisions |

**PRD decision rule:** At least three of the above must be implemented and documented. Domain choice drives which three are most relevant.

---

## 9. Performance Targets

| Metric | Target |
|--------|--------|
| End-to-end latency (single-tool) | <5 s |
| Multi-step latency (3+ tools) | <15 s |
| Tool success rate | >95% |
| Eval pass rate | >80% |
| Hallucination rate | <5% unsupported claims |
| Verification accuracy | >90% correct flags |

**PRD decision rule:** Use these in evals and in observability dashboards; report in Agent Architecture Doc and cost analysis.

---

## 10. AI Cost Analysis (Required Deliverable)

### 10.1 Development & Testing

- LLM API costs (reasoning, tool calls, response generation)  
- Total tokens (input/output breakdown)  
- Number of API calls during development and testing  
- Observability tool costs (if any)  

### 10.2 Production Projections

| Scale | Monthly cost |
|-------|----------------|
| 100 users | $___/month |
| 1,000 users | $___/month |
| 10,000 users | $___/month |
| 100,000 users | $___/month |

**Include:** queries per user per day, average tokens per query (in + out), tool call frequency, verification overhead.

---

## 11. Stack & Framework Decisions (Pre-Search)

### 11.1 Agent Framework (choose one)

| Option | Best for |
|--------|----------|
| LangChain | Flexible agents, tool integrations, docs |
| LangGraph | Multi-step workflows, state machines, cycles |
| CrewAI | Multi-agent, roles |
| AutoGen | Conversational, code execution, Microsoft |
| Semantic Kernel | Enterprise, .NET/Python, plugins |
| Custom | Full control, learning |

**PRD decision rule:** Recommended path = LangChain or LangGraph. Document choice and rationale in Pre-Search output.

### 11.2 Technical Stack (Recommended)

| Layer | Suggested |
|-------|-----------|
| Agent framework | LangChain or LangGraph |
| LLM | GPT-5, Claude, or open source (Llama 3, Mistral) |
| Observability | LangSmith or Braintrust |
| Evals | LangSmith Evals, Braintrust Evals, or custom |
| Backend | Python/FastAPI or Node.js/Express |
| Frontend | React (Vite), Next.js, or similar |
| Deployment | Vercel, Railway, Modal, or cloud |

**PRD decision rule:** Use whatever stack lets you ship. Pre-Search should lock these and document in submission.

---

## 12. Build Priority Order (Reference for Roadmap)

1. **Basic agent** — Single tool call working end-to-end  
2. **Tool expansion** — Remaining tools; verify each  
3. **Multi-step reasoning** — Agent chains tools correctly  
4. **Observability** — Tracing and visibility  
5. **Eval framework** — Test suite, baseline metrics  
6. **Verification layer** — Domain-specific checks  
7. **Iterate on evals** — Improve agent from failures  
8. **Open source prep** — Package and document for release  

**Critical:** One tool fully working before adding more; observability early; evals incrementally; adversarial testing throughout; document failure modes for verification design.

---

## 13. Open Source Contribution (Required — One of)

| Type | Requirement |
|------|-------------|
| New agent package | Publish domain agent (npm, PyPI) |
| Eval dataset | Release test suite as public dataset |
| Framework contribution | PR to LangChain, LlamaIndex, etc. |
| Tool integration | Reusable tool for domain |
| Documentation | Public guide/tutorial |

**PRD decision rule:** Choose one and plan in Pre-Search; link in final submission.

---

## 14. Submission Checklist (Final — Sunday 10:59 PM CT)

| Deliverable | Required |
|-------------|----------|
| **GitHub repository** | Setup guide, architecture overview, deployed link |
| **Demo video (3–5 min)** | Agent in action, eval results, observability dashboard |
| **Pre-Search document** | Completed checklist Phase 1–3 (saved AI conversation) |
| **Agent Architecture Doc** | 1–2 pages (domain, architecture, verification, eval results, observability, open source) |
| **AI Cost Analysis** | Dev spend + 100/1K/10K/100K projections |
| **Eval dataset** | 50+ test cases with results |
| **Open source link** | Package, PR, or public dataset |
| **Deployed application** | Publicly accessible agent interface |
| **Social post** | X or LinkedIn: description, features, demo/screenshots, tag @GauntletAI |

---

## 15. Agent Architecture Doc Template (1–2 Pages)

| Section | Content |
|---------|---------|
| Domain & use cases | Why this domain; specific problems solved |
| Agent architecture | Framework, reasoning, tool design |
| Verification strategy | Checks implemented and why |
| Eval results | Test suite results, pass rates, failure analysis |
| Observability setup | What’s tracked; insights |
| Open source contribution | What was released; where to find it |

---

## 16. Pre-Search Checklist (Complete Before Code)

- **Phase 1 — Constraints:** Domain, scale, reliability, team/skills (items 1–4).  
- **Phase 2 — Architecture:** Framework, LLM, tools, observability, eval, verification (items 5–10).  
- **Phase 3 — Refinement:** Failure modes, security, testing, open source, deployment, iteration (items 11–16).  

Save the Pre-Search AI conversation as the reference document for the submission.

---

## 17. Interview Prep (Reference)

- **Technical:** Framework choice, tool design, verification and failure modes, eval methodology, scaling to production.  
- **Mindset:** Domain complexity, iteration from eval failures, learning, handling ambiguity and pressure.  

---

*This PRD is the single source of truth for scope, gates, and decisions. Refer to it when prioritizing work and validating deliverables.*
