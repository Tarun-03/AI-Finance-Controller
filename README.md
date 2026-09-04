# AI Finance Controller

An **agentic AI finance-operations platform** for automated reconciliation, exception investigation, and human-in-the-loop financial controls.

> **Project status:** Local development / demo project.
---

## 1. What does this project solve?

Finance teams often have to manually compare transaction, payment, settlement, and invoice records. When values do not match, someone has to investigate the exception, determine the reason, check the applicable finance policy, and decide whether it can be resolved.

**AI Finance Controller** automates this workflow.

It can:

- Reconcile financial records across multiple sources.
- Detect exceptions such as:
  - `AMOUNT_MISMATCH`
  - `FEE_MISMATCH`
  - `STATUS_MISMATCH`
  - `MISSING_PAYMENT`
  - `MISSING_SETTLEMENT`
  - `MISSING_INVOICE`
- Investigate exceptions using an AI agent.
- Retrieve relevant finance policies/context using **RAG**.
- Recommend `AUTO_RESOLVE` or `HUMAN_REVIEW`.
- Apply deterministic finance rules and guardrails before an action is finalized.
- Allow a human reviewer to approve or reject exceptions.
- Maintain an audit trail of important system, agent, policy, and human actions.

The key design principle is:

> **The LLM assists with investigation and reasoning, while deterministic finance rules, guardrails, and human approval control financial actions.**

---

## 2. High-level architecture

```text
                         ┌──────────────────────────┐
                         │      React Frontend      │
                         │   TypeScript + Vite      │
                         └────────────┬─────────────┘
                                      │ REST API
                                      ▼
                         ┌──────────────────────────┐
                         │      FastAPI Backend     │
                         │      API / Services      │
                         └────────────┬─────────────┘
                                      │
                  ┌───────────────────┼───────────────────┐
                  ▼                   ▼                   ▼
          ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
          │ Reconciliation│    │ AI Agent     │    │ Guardrails   │
          │ Engine        │    │ LangGraph    │    │ + Policies   │
          └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
                 │                   │                   │
                 │                   ▼                   │
                 │           ┌──────────────┐            │
                 │           │ RAG / Policy │            │
                 │           │ Retrieval    │            │
                 │           └──────────────┘            │
                 │                                       │
                 └───────────────────┬───────────────────┘
                                     ▼
                            ┌──────────────────┐
                            │ Database / Audit │
                            │ Logs / Exceptions│
                            └──────────────────┘
```

---

## 3. Agentic AI workflow

The project uses an agentic workflow rather than a simple chatbot.

A typical exception goes through:

```text
Financial Records
       │
       ▼
Reconciliation
       │
       ├── Match ───────────────► Completed
       │
       └── Mismatch
              │
              ▼
       Create Exception
              │
              ▼
       AI Investigation
              │
              ├── Retrieve relevant policy/context (RAG)
              │
              ├── Analyze exception
              │
              ├── Calculate/assess risk
              │
              └── Recommend action
                       │
              ┌────────┴────────┐
              ▼                 ▼
        AUTO_RESOLVE       HUMAN_REVIEW
              │                 │
       Deterministic       Human approves/
       rules + guardrails  rejects
              │                 │
              └────────┬────────┘
                       ▼
                  Audit Log
```

### Why human-in-the-loop?

Financial operations should not allow an LLM to freely modify financial outcomes.

For lower-risk cases, the system can recommend automatic resolution when the exception falls within configured rules and thresholds.

For higher-risk or ambiguous cases, the system requires a human decision.

---

## 4. Technology stack

### Frontend

- React
- TypeScript
- Vite
- CSS

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic

### Agentic AI

- LangGraph for the agent workflow/state graph
- LangChain components for LLM/tool/retrieval integration
- RAG for retrieving relevant finance policy/context
- Agent tools for investigation and finance operations

### Controls

- Deterministic finance rules
- Guardrails
- Human-in-the-loop approval/rejection
- Audit logging

### Database

The backend uses SQLAlchemy-based persistence for transactions, reconciliation records, exceptions, and audit information.

---

## 5. Repository structure

```text
ai-finance-controller/
│
├── backend/
│   └── app/
│       ├── agents/
│       │   ├── graph.py
│       │   ├── nodes.py
│       │   ├── prompts/
│       │   └── tools/
│       │
│       ├── api/
│       │   └── routes/
│       │
│       ├── core/
│       ├── db/
│       ├── guardrails/
│       ├── mcp/
│       │   └── tools/
│       ├── models/
│       ├── rag/
│       ├── repositories/
│       ├── schemas/
│       ├── seed/
│       ├── services/
│       └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── finance.ts
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.tsx
│   └── package.json
│
└── README.md
```

---

# 6. Running the project locally

## Prerequisites

Install:

- Python 3.11+ recommended
- Node.js 18+ recommended
- npm
- Git
- A configured database supported by the project
- Any required LLM/API credentials used by your local backend configuration

Check:

```bash
python3 --version
node --version
npm --version
git --version
```

---

# 7. Clone the repository

Replace `<YOUR-GITHUB-REPOSITORY>` with the repository URL.

```bash
git clone <YOUR-GITHUB-REPOSITORY>
cd ai-finance-controller
```

If your repository has a different name, enter that directory instead.

---

# 8. Backend setup

From the project root:

```bash
cd backend
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

If the project uses a `.env` file, create/configure it according to the variables expected by the backend.

For example:

```bash
cp .env.example .env
```

Only run the command above if `.env.example` exists in the repository.

---

# 9. Database / seed data

The project includes seed functionality for generating synthetic finance data.

From the project root, the seed command used during development is:

```bash
python3 -m app.seed.seed_database
```

This generates synthetic transactions and exception scenarios for the demo.

The demo data contains scenarios such as:

```text
MATCHED
AMOUNT_MISMATCH
FEE_MISMATCH
STATUS_MISMATCH
MISSING_PAYMENT
MISSING_SETTLEMENT
MISSING_INVOICE
```

> Do not use the synthetic seed data as production financial data.

---

# 10. Start the backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

The API should normally be available at:

```text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation should normally be available at:

```text
http://127.0.0.1:8000/docs
```

The exact host/port can be changed if your backend configuration uses different values.

---

# 11. Start the frontend

Open another terminal.

From the project root:

```bash
cd frontend
```

Install frontend dependencies:

```bash
npm install
```

Start Vite:

```bash
npm run dev
```

Open the URL printed by Vite, usually:

```text
http://localhost:5173
```

---

# 12. Build the frontend

Before submitting or deploying the frontend:

```bash
cd frontend
npm run build
```

A successful build should finish with a Vite production build message and generate the `dist/` directory.

You can also preview the production build locally:

```bash
npm run preview
```

---

# 13. Recommended demo flow

The easiest way to demonstrate the project is:

### Step 1 — Dashboard

Show:

- Total transactions
- Open exceptions
- Investigating exceptions
- Resolved exceptions
- System health
- Priority exceptions

Explain:

> "This dashboard gives the finance operations team a real-time view of reconciliation health and outstanding exceptions."

### Step 2 — Run reconciliation

Click:

**Run Reconciliation**

Explain:

> "The reconciliation engine compares records across the available financial sources and identifies matched transactions and exceptions."

### Step 3 — Open Exceptions

Go to:

**Exceptions**

Show different exception types and severities.

For example:

```text
AMOUNT_MISMATCH
FEE_MISMATCH
STATUS_MISMATCH
```

Explain:

> "Instead of asking a finance analyst to manually find these discrepancies, the system automatically creates structured exception records."

### Step 4 — AI Investigation

Open an exception and show:

- Agent analysis
- Reasoning
- Recommended action
- Confidence
- Risk score
- Guardrail status

Explain:

> "The AI investigation agent analyzes the exception and retrieves relevant policy context using RAG. The agent then recommends an action."

### Step 5 — Explain AUTO_RESOLVE

For a low-risk exception:

```text
Recommended Action: AUTO_RESOLVE
```

Explain:

> "If the difference falls within the configured finance threshold and the deterministic guardrails pass, the exception can be considered for automatic resolution."

### Step 6 — Explain HUMAN_REVIEW

For a higher-risk exception:

```text
Recommended Action: HUMAN_REVIEW
```

Explain:

> "If the exception is outside the automatic resolution range or requires a human decision, the workflow stops and asks a finance user to approve or reject it."

### Step 7 — Approve / Reject

Demonstrate the human-in-the-loop action.

Explain:

> "The LLM does not have unrestricted authority to finalize a financial decision. A human can approve or reject the proposed resolution."

### Step 8 — Auditability

Show the audit information.

Explain:

> "Important actions are recorded so we can trace reconciliation, agent decisions, policy checks, tool executions, and manual overrides."

---

# 14. Example exception explanation

Suppose the system shows:

```text
Expected amount: ₹1,000
Actual amount:   ₹1,100
Difference:      ₹100
Type:            AMOUNT_MISMATCH
```

The agent investigates the discrepancy.

If the configured policy allows a ₹100 difference to be automatically resolved:

```text
Recommended Action: AUTO_RESOLVE
Guardrail: PASSED
```

The system can proceed according to the deterministic policy.

For a larger or higher-risk difference:

```text
Recommended Action: HUMAN_REVIEW
```

The exception is presented to a finance user instead.

---

# 15. RAG in this project

**RAG = Retrieval-Augmented Generation.**

Instead of asking the LLM to make a decision entirely from its pretrained knowledge, the application retrieves relevant finance-policy information and provides that context to the agent.

Conceptually:

```text
Exception
   │
   ▼
Retrieve relevant policy/context
   │
   ▼
Context + Exception Data
   │
   ▼
LLM / Agent
   │
   ▼
Investigation + Recommendation
```

RAG is particularly useful here because finance decisions should be based on the application's current policies and rules rather than generic LLM knowledge.

---

# 16. Why LangGraph / agentic AI?

A normal LLM call might look like:

```text
Question → LLM → Answer
```

This project uses a workflow closer to:

```text
Exception
   ↓
Investigate
   ↓
Retrieve context
   ↓
Evaluate policy
   ↓
Assess risk
   ↓
Apply guardrails
   ↓
Recommend action
   ↓
Human approval if required
   ↓
Audit
```

This makes the system more suitable for structured finance operations.

---

# 17. Safety and guardrails

The project intentionally separates:

### AI reasoning

Used for:

- Investigation
- Explanation
- Contextual reasoning
- Recommendation

### Deterministic controls

Used for:

- Financial thresholds
- Policy checks
- Risk controls
- Approval requirements
- Final action constraints

This reduces the risk of an LLM making an uncontrolled financial decision.

---

# 18. Human-in-the-loop

The workflow supports human approval for exceptions that should not be resolved automatically.

Possible outcomes include:

```text
APPROVE
REJECT
ESCALATE
```

The backend records the reviewer and reason where applicable.

This provides a controlled transition:

```text
AI recommendation
       ↓
Policy / Guardrail check
       ↓
Human approval
       ↓
Final resolution
```

---

# 19. Audit logging

The system records important events using audit actions such as:

```text
RECONCILIATION_STARTED
RECONCILIATION_COMPLETED
EXCEPTION_CREATED
EXCEPTION_UPDATED
EXCEPTION_RESOLVED
AGENT_DECISION
TOOL_EXECUTED
POLICY_CHECK
MANUAL_OVERRIDE
```

This is important for financial systems because a reviewer should be able to understand **what happened, what the agent recommended, what controls were applied, and whether a human overrode the recommendation.**

---

# 20. Development validation

Python syntax can be checked with:

```bash
python3 -m compileall backend/app
```

Frontend production build:

```bash
cd frontend
npm run build
```

Both should complete successfully before pushing changes.

---

# 21. Current deployment status

This repository is currently intended to be run locally.

```text
Frontend:  Local Vite development server
Backend:   Local FastAPI server
Database:  Local/configured database
Hosting:   Not currently deployed
```

The application can later be deployed using services such as Vercel for the frontend and Render for the backend, but deployment configuration is not included in this repository status.

---

# 22. Limitations

This is a finance-operations prototype/demo using synthetic data.

It should not be treated as a production financial system without additional work around:

- Authentication and authorization
- Secrets management
- Production database configuration
- Observability and monitoring
- Rate limiting
- Data privacy
- Stronger financial controls
- Production-grade testing
- Failure recovery
- Security hardening
- Compliance requirements
- Production LLM/provider configuration

---

# 23. Quick start

For experienced developers:

### Terminal 1 — Backend

```bash
git clone <YOUR-GITHUB-REPOSITORY>
cd ai-finance-controller

cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 -m app.seed.seed_database

uvicorn app.main:app --reload
```

### Terminal 2 — Frontend

```bash
cd ai-finance-controller/frontend
npm install
npm run dev
```

Then open the Vite URL shown in the terminal.

---

## 24. Project objective in one sentence

> **AI Finance Controller is an agentic AI platform that automates financial reconciliation and exception investigation while combining RAG, deterministic finance policies, guardrails, and human-in-the-loop approval to make financial operations faster, explainable, and auditable.**

---

## License

Add the appropriate license for your repository if required.
