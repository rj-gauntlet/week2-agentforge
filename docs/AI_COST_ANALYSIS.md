# AgentForge — AI Cost Analysis

**Version:** 1.0 (Final Submission)  
**Purpose:** Document the development API spend and project the estimated API and operational costs for production scaling (100 to 100,000 users).  

---

## 1. Development Spend (Actuals)

During the one-week sprint, we logged every LLM execution via our custom `cost_logging.py` module, which extracts exact token usage from LangChain traces and calculates the estimated cost based on the chosen model's pricing.

**Model Used:** OpenAI `gpt-4o` (Pricing: $2.50 / 1M input tokens, $10.00 / 1M output tokens).

### **Totals (via `data/cost_log.jsonl`)**
- **Total Requests Logged:** 119
- **Total Input Tokens:** 238,771
- **Total Output Tokens:** 9,946
- **Total Estimated LLM Cost:** **$0.69**

*Note: The actual OpenAI API billing dashboard shows approximately $5.01 total spend for the entire sprint, which includes exploratory manual testing, tool failures during initial setup, and runs before the cost logger was implemented on Day 5. The $0.69 represents the cost of 119 successful, fully-instrumented end-to-end agent runs (including full 56-case eval harness runs).*

---

## 2. Production Cost Projections

To estimate production costs, we must define the average usage per user and the average token cost per query.

### **Assumptions & Averages**
1. **Model:** OpenAI `gpt-4o` (or equivalent like Claude 3.5 Sonnet).
2. **Average Query Profile:** Based on our logs, a typical multi-step query against our MVP toolset requires:
   - **Input:** ~2,000 tokens (system prompt + conversation history + tool descriptions).
   - **Output:** ~85 tokens (tool calls + final synthesized answer).
   - **Cost per query:** ~$0.0058 (using gpt-4o pricing).
3. **Usage Volume:** In a clinical/administrative setting (e.g., OpenEMR), we assume **10 queries per user per day**.
4. **Monthly Factor:** 20 working days per month per user.
5. **Total queries per user per month:** 200.
6. **LLM Cost per user per month:** 200 queries * $0.0058 = **$1.16**.

### **Infrastructure Overheads**
Beyond LLM token costs, scaling requires backend compute (FastAPI) and observability (LangSmith).
- **Backend (Railway/Vercel):** ~$5/mo for baseline; scales linearly with traffic.
- **Observability (LangSmith):** $39/user/month (Plus tier) + $0.50 per 1k traces over the free limit.

---

### **Cost Table by Scale**

| Scale             | Monthly Queries | Monthly LLM Cost | Observability (Est)              | Compute (Est) | Total Est. Cost / Mo | Cost per User |
| :---------------- | :-------------- | :--------------- | :------------------------------- | :------------ | :------------------- | :------------ |
| **100 users**     | 20,000          | **$116**         | $39 (Base plan)                  | $5            | **$160**             | $1.60         |
| **1,000 users**   | 200,000         | **$1,160**       | $139 ($39 base + $100 overage)   | $50           | **$1,349**           | $1.35         |
| **10,000 users**  | 2,000,000       | **$11,600**      | $1,039 ($39 base + $1k overage)  | $500          | **$13,139**          | $1.31         |
| **100,000 users** | 20,000,000      | **$116,000**     | Enterprise Pricing               | $5,000        | **$121,000+**        | ~$1.21        |

---

## 3. Cost Optimization Strategies for Scaling

To significantly reduce the $1.16/user/mo LLM cost at the 10,000+ user scale, the following optimizations should be implemented:

1. **Model Routing:** Not all queries require GPT-4o. Simple lookups (e.g., `procedure_lookup`) could be routed to `gpt-4o-mini` or `Claude 3.5 Haiku` (which cost ~90% less), reserving the heavy, expensive models exclusively for complex `drug_interaction_check` or multi-step reasoning queries.
2. **Context Window Trimming:** The system prompt and tool schemas currently consume ~1,500 of the 2,000 input tokens. Summarizing chat history and dynamically loading only relevant tool schemas (rather than passing all 8 tools every time) could reduce input token volume by 50%.
3. **Semantic Caching:** Common queries (e.g., "What is the code for knee replacement?") can be cached using Redis and semantic similarity (e.g., LangChain's `SemanticCache`). If a 95% similar query was asked recently, return the cached result instead of hitting the LLM, effectively reducing the cost of that query to $0.