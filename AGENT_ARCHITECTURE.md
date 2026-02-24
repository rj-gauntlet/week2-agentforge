# Agent Architecture Document

**Version:** 1.0
**Domain:** Healthcare (OpenEMR)

## 1. System Overview

AgentForge Clinical is an autonomous healthcare assistant designed to support administrative and clinical workflows. It uses a Large Language Model (LLM) equipped with reasoning capabilities and a specific suite of tool integrations to fetch data safely, synthesize information, and provide structured, accurate responses without hallucinations.

### 1.1 Core Components

*   **Reasoning Engine:** LangChain orchestration powered by `gpt-4o` or `claude-sonnet-4`.
*   **Orchestrator:** A stateless `create_agent` implementation that receives a user query and the chat history, decides if/which tools to execute, parses their outputs, and formulates a final response.
*   **Memory:** Maintained via standard LangChain message structures (HumanMessage, AIMessage, ToolMessage) passed iteratively into the orchestrator.
*   **Tools:** A suite of 6 domain-specific functions (see below).
*   **Verification Layer:** A combination of system prompts and deterministic tool-level assertions to prevent misdiagnosis.
*   **Observability:** Full integration with LangSmith for traces, latency metrics, token tracking, and structured evaluation harness.

---

## 2. Tool Registry

The agent has access to the following 6 tools. All tools return standardized `tool_result` JSON schemas ensuring the orchestrator always receives structured data.

1.  **`drug_interaction_check` (Hero Tool)**
    *   **Data Source:** Live openFDA API (`https://api.fda.gov/drug/label.json`). Includes graceful fallback to a local mock dataset if the API is unreachable.
    *   **Purpose:** Checks for severe interactions (e.g. bronchospasm warnings) between a list of provided medications.
2.  **`procedure_lookup`**
    *   **Data Source:** Mock dataset (`data/procedures.json`).
    *   **Purpose:** Resolves natural language procedure descriptions (e.g. "Knee Replacement") into standardized CPT billing codes (e.g., "27447") to assist other tools.
3.  **`symptom_lookup`**
    *   **Data Source:** Mock dataset (`data/symptom_lookup.json`).
    *   **Purpose:** Triage only. Maps symptoms to possible underlying causes and an urgency score.
4.  **`provider_search`**
    *   **Data Source:** Mock dataset (`data/providers.json`).
    *   **Purpose:** Filters available doctors based on location and specialty.
5.  **`appointment_availability`**
    *   **Data Source:** Mock dataset (`data/appointment_slots.json`).
    *   **Purpose:** Retrieves schedule openings for specific providers on specific dates.
6.  **`insurance_coverage_check`**
    *   **Data Source:** Mock dataset (`data/insurance_coverage.json`).
    *   **Purpose:** Verifies if a specific CPT procedure code is covered under a patient's insurance plan.

---

## 3. Verification & Safety Layer

To guarantee clinical safety and minimize hallucinations, the agent employs a 3-layer verification approach:

### 1. Domain Constraints (System Prompt)
The Orchestrator's `SYSTEM_PROMPT` enforces hard boundaries:
*   *"Do not give dosing advice or diagnose conditions."*
*   *"If the user asks a question entirely unrelated to healthcare... you must politely refuse to answer."*

### 2. Structured Output Assertions (Tool Level)
Tools inject explicit safety flags into their JSON outputs that force the agent into a compliant state. For example, `symptom_lookup` and `drug_interaction_check` both return:
```json
{
    "can_diagnose": false,
    "requires_provider_consultation": true
}
```

### 3. Graceful Fallbacks
The hero tool (`drug_interaction_check`) wraps its live API call in a `try/except` block with a short timeout. If the openFDA API experiences an outage, it seamlessly falls back to querying the local JSON dataset, preventing an agent crash.

---

## 4. Evaluation Framework

The project utilizes **LangSmith Evals** to run a deterministic, automated test suite against the agent.

*   **Test Dataset:** `data/eval_cases.json` contains 18 cases spanning Happy Path, Multi-step reasoning, Edge cases, and Adversarial attacks.
*   **Evaluation Script:** `scripts/run_evals.py` builds the LangSmith dataset, runs the agent against each query, and grades the performance.
*   **Grading Mechanics:** We explicitly avoid using an "LLM-as-a-judge" due to latency, cost, and non-determinism. Instead, custom Python evaluators check:
    1.  Did the agent invoke the exact `expected_tools`?
    2.  Did the agent's final text output contain the `expected_keywords`?
    3.  Did the tools emit the correct `expected_flags` (e.g. `"can_diagnose": false`) to ensure safety?

---

## 5. Deployment & UIs

The core API is built on FastAPI. The system currently features multiple front-end integrations:
1.  **Streamlit Chat Dashboard:** A comprehensive web UI featuring a live telemetry sidebar that exposes the exact JSON inputs and outputs of the agent's tool calls in real-time.
2.  **Twilio SMS / WhatsApp Bot:** A webhook integration allowing users to query the agent directly from their mobile devices via the Twilio platform.
