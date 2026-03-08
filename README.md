# CASA — AI-Powered Loan Origination System

> **Credit Assessment and Servicing Automation**  
> The world's first AI-powered loan origination system for FDIC-insured community banks.

## Architecture Overview

CASA uses a **multi-agent architecture** where six specialized AI agents handle discrete
components of the loan origination lifecycle, coordinated through an event-driven orchestration layer.

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │Application│ │ Dashboard│ │Sarah Chat│ │  Audit Trail  │  │
│  │   Form   │ │ Pipeline │ │ Console  │ │    Viewer     │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP / REST API
┌──────────────────────┴──────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Orchestrator Agent                       │   │
│  │     (State Machine · Task Dispatch · Escalation)     │   │
│  └──────┬────────┬────────┬────────┬────────┬───────────┘   │
│         │        │        │        │        │               │
│  ┌──────┴──┐ ┌───┴───┐ ┌──┴───┐ ┌──┴──┐ ┌──┴───┐          │
│  │  Sarah  │ │Compli-│ │Under-│ │ Doc │ │Price │          │
│  │Engaging │ │ ance  │ │write │ │Intel│ │Agent │          │
│  └─────────┘ └───────┘ └──────┘ └─────┘ └──────┘          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Infrastructure: SQLite · Audit Log · LLM Gateway    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## AI Model Recommendations Per Agent

| Agent | Recommended Models | Why | Fallback |
|---|---|---|---|
| **Sarah (Engagement)** | `claude-sonnet-4-20250514` / `gpt-4o` | Excellent conversational ability, empathy, domain understanding | `claude-haiku-4-5-20251001` for high-volume SMS (lower cost) |
| **Compliance Agent** | `claude-sonnet-4-20250514` + deterministic rules | Entity extraction + rule engine hybrid; LLM parses unstructured data, rules enforce SBA SOP | Rule-engine-only mode (no LLM needed for watchlist matching) |
| **Underwriting Agent** | `claude-sonnet-4-20250514` for narrative / `gpt-4o` for extraction | Narrative memo generation needs strong writing; extraction needs structured output | `claude-haiku-4-5-20251001` for extraction; deterministic engine for all calculations |
| **Document Intelligence** | `claude-sonnet-4-20250514` (vision) / Google Document AI / AWS Textract | Claude's vision handles mixed documents; dedicated OCR services for production scale | `tesseract` (open-source OCR) + `layoutlm` for field extraction |
| **Pricing Agent** | Deterministic engine + `claude-haiku-4-5-20251001` | Pricing must be deterministic; LLM only formats term sheets | No LLM needed for core pricing math |
| **Orchestrator** | No LLM needed | Pure state machine + event routing; deterministic by design | N/A |

### Model Selection Principles

1. **Never use LLMs for financial calculations** — DSCR, add-backs, and scoring use deterministic engines
2. **LLMs handle language tasks** — extraction, narrative generation, conversation, classification
3. **Confidence scoring on all LLM outputs** — low-confidence values route to human review
4. **Cost optimization** — use smaller models (Haiku) for high-volume, low-complexity tasks
5. **Fallback chains** — every LLM call has a fallback model and a no-LLM degraded mode

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend API** | Python 3.11+ · FastAPI · Uvicorn |
| **Frontend** | Python · Streamlit (multi-page app) |
| **Database** | SQLite (MVP) → PostgreSQL (production) |
| **LLM Integration** | LiteLLM (unified interface to Claude, GPT-4, local models) |
| **Task Queue** | In-process async (MVP) → Celery + Redis (production) |

---

## Quick Start

### Prerequisites

- Python 3.11+
- An API key for at least one LLM provider (Anthropic, OpenAI, or Google)

### Installation

```bash
git clone <repo-url>
cd casa-mvp

python -m venv venv
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

cp .env.example .env
# Edit .env with your API keys
```

### Running the Application

```bash
# Terminal 1: Start the backend API
uvicorn backend.main:app --reload --port 8000

# Terminal 2: Start the frontend
streamlit run frontend/app.py --server.port 8501
```

Open **http://localhost:8501** in your browser.

---

## Project Structure

```
casa-mvp/
├── backend/
│   ├── main.py                  # FastAPI entry point
│   ├── config.py                # Configuration & env vars
│   ├── database.py              # SQLite setup & ORM models
│   ├── agents/
│   │   ├── base_agent.py        # Abstract base agent class
│   │   ├── sarah_agent.py       # Engagement & churn recovery
│   │   ├── compliance_agent.py  # KYB/KYC, watchlist, SBA SOP
│   │   ├── underwriting_agent.py# Financial spreading, DSCR
│   │   ├── document_agent.py    # OCR, classification, extraction
│   │   ├── pricing_agent.py     # Rate calc, term sheet generation
│   │   └── orchestrator.py      # State machine & coordination
│   ├── api/
│   │   ├── applications.py      # Loan application endpoints
│   │   ├── dashboard.py         # Dashboard data endpoints
│   │   ├── chat.py              # Sarah chat endpoints
│   │   └── documents.py         # Document upload endpoints
│   ├── core/
│   │   ├── llm_gateway.py       # Unified LLM interface with fallbacks
│   │   ├── audit_log.py         # Immutable audit logging
│   │   └── state_machine.py     # Loan lifecycle states
│   └── models/
│       └── schemas.py           # Pydantic models
├── frontend/
│   ├── app.py                   # Streamlit main app (home)
│   └── pages/
│       ├── 1_📋_Application.py  # Loan application form
│       ├── 2_💬_Sarah_Chat.py   # Chat with Sarah
│       ├── 3_📊_Dashboard.py    # Loan officer dashboard
│       └── 4_📜_Audit_Trail.py  # Audit log viewer
├── tests/
│   └── test_agents.py
├── docs/
│   └── AGENT_MODELS.md          # Detailed model guide per agent
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Development Roadmap

### Phase 1 — Foundation (This MVP)
- [x] Orchestrator state machine with loan lifecycle
- [x] Sarah engagement agent with chat and churn detection
- [x] Smart application form with progressive disclosure
- [x] LLM Gateway with fallback routing
- [x] Immutable audit logging
- [x] Loan officer pipeline dashboard

### Phase 2 — Intelligence
- [ ] Document OCR pipeline (Textract / Document AI)
- [ ] Compliance Agent — live KYB/KYC API integrations
- [ ] Watchlist screening (OFAC SDN, BIS Entity List)

### Phase 3 — Automation
- [ ] Underwriting Agent — full DSCR, financial spreading
- [ ] Pricing Agent — market rate feeds, live term sheets
- [ ] Full analytics dashboard

### Phase 4 — Scale
- [ ] PostgreSQL + Kafka migration
- [ ] Multi-tenant architecture
- [ ] Core banking system integrations
- [ ] Kubernetes deployment

---

## License

Proprietary — All rights reserved.
