# Agent Architecture Document

## 1. Domain & Purpose
This agent serves as a healthcare assistant for a clinical setting. It is designed to assist users with specific clinical and administrative tasks while strictly adhering to safety guidelines and avoiding medical diagnosis or dosing advice.

The agent's primary capabilities include:
- Checking drug interactions.
- Looking up symptoms (providing possible conditions and urgency, not diagnoses).
- Searching for healthcare providers by specialty and location.
- Checking appointment availability.
- Verifying insurance coverage for procedures.
- Looking up medical procedure codes (CPT).

## 2. Architecture Overview
The system is built using a LangChain agent orchestrator integrated with a FastAPI backend and a Streamlit frontend. 

- **Orchestrator (`agent/orchestrator.py`):** Manages the conversation flow, invokes the LLM (OpenAI GPT-4o or Anthropic Claude), and handles tool execution. It also enforces system prompts and verification steps.
- **Tools (`agent/tools/`):** A suite of specialized Python functions that interact with mock data or external APIs to perform the agent's core capabilities.
- **Backend (`main.py`):** A FastAPI application that exposes endpoints for chat (`/chat`), health checks (`/health`), and user feedback (`/feedback`).
- **Frontend (`streamlit_app.py`):** A Streamlit-based web interface that provides a chat UI, displays tool usage, and collects user feedback.

## 3. Verification & Safety

To ensure the agent operates safely and securely within its defined domain, we have implemented a multi-layered verification system. These checks occur both before the user's query is sent to the LLM and after the LLM generates a response.

### 3.1 Pre-LLM Verification (Input Checks)

*   **Input Domain & Jailbreak Prevention (`_verify_input_domain`):**
    *   **Purpose:** To catch blatant adversarial requests, prompt injections, or attempts to force the agent out of its clinical persona.
    *   **Mechanism:** A heuristic check that scans the user's input for forbidden keywords (e.g., "ignore previous", "system prompt", "hack", "bypass", "talk like", "act like", "pirate").
    *   **Action:** If triggered, the system immediately rejects the request with a standard refusal message before invoking the LLM.

*   **PHI Redaction (`_verify_phi_redaction`):**
    *   **Purpose:** To protect sensitive Protected Health Information (PHI) and Personally Identifiable Information (PII) from being sent to external LLM APIs.
    *   **Mechanism:** Regular expressions are used to identify and mask sensitive patterns in the user's query.
        *   Social Security Numbers (SSNs) are replaced with `[REDACTED SSN]`.
        *   Phone numbers are replaced with `[REDACTED PHONE]`.
        *   Dates of Birth (only when preceded by keywords like "DOB" or "born on" to avoid redacting appointment dates) are replaced with `[REDACTED DOB]`.
    *   **Action:** The sanitized query is passed to the LLM.

### 3.2 Post-LLM Verification (Output Checks)

*   **Fact-Checking Against Tool Output (`_verify_fact_check`):**
    *   **Purpose:** To detect and mitigate LLM hallucinations, specifically ensuring the LLM does not exaggerate or misrepresent the data returned by the tools.
    *   **Mechanism:** After the LLM generates a response, the system reviews the tool messages from that turn. For example, if the `drug_interaction_check` tool returned a "minor" severity, but the LLM's output contains words like "fatal" or "major", a hallucination is suspected.
    *   **Action:** If a contradiction is found, a warning message is appended to the LLM's output: `\n\n(Fact-Check Error: The LLM severity description contradicts the tool's 'minor' rating. Please verify.)`

*   **Output Safety & Clinical Disclaimer (`_verify_output_safety`):**
    *   **Purpose:** To ensure that any discussion of clinical topics includes a mandatory medical disclaimer.
    *   **Mechanism:** The system scans the LLM's final output for clinical keywords (e.g., "symptom", "treatment", "diagnosis", "condition", "pain", "medication").
    *   **Action:** If clinical keywords are found and the output does not already contain a disclaimer, the system appends: `\n\n[Disclaimer: This information is for educational purposes and is not a medical diagnosis. Please consult a healthcare provider.]`

## 4. Evaluation & Observability
*(To be completed)*

## 5. Open Source Plan
*(To be completed)*
