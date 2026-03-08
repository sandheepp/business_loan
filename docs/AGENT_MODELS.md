# CASA — AI Model Guide Per Agent

This document provides detailed guidance on which AI models to use for each agent,
including cost estimates, latency expectations, and implementation notes.

---

## 1. Sarah — Engagement Agent

| Task | Model | Latency | Notes |
|---|---|---|---|
| **Real-time chat** | `claude-sonnet-4-20250514` | 1–3s | Best conversational quality |
| **Churn SMS** | `claude-haiku-4-5-20251001` | <1s | High volume, lower cost |
| **Sentiment analysis** | `claude-haiku-4-5-20251001` | <1s | Classify frustration level |
| **Fallback** | `gpt-4o-mini` | <1s | If Anthropic API is down |

Sarah uses a system prompt with lending domain knowledge and strict guardrails.
She NEVER provides financial advice. Churn detection is rule-based (inactivity timers).

---

## 2. Compliance Agent

| Task | Model | Notes |
|---|---|---|
| **SBA SOP eligibility** | Deterministic rule engine | No LLM needed |
| **SPSS scoring** | Deterministic calculator | SBA formula, min 165 |
| **Watchlist matching** | Fuzzy string matching | OFAC SDN, no LLM |
| **KYB entity extraction** | `claude-sonnet-4-20250514` | Parse SOS filings |
| **Report narrative** | `claude-sonnet-4-20250514` | Human-readable report |

---

## 3. Underwriting Agent

| Task | Model | Notes |
|---|---|---|
| **Tax return extraction** | `claude-sonnet-4-20250514` (vision) | Read PDFs |
| **Financial spreading** | Deterministic engine | Standardized chart of accounts |
| **DSCR calculation** | Deterministic engine | Never use LLM for math |
| **Credit policy scoring** | Weighted formula | Configurable per bank |
| **Underwriting memo** | `claude-sonnet-4-20250514` | Narrative generation |

**Critical: ALL financial calculations are deterministic. LLM only extracts and narrates.**

---

## 4. Document Intelligence Agent

| Task | Model | Notes |
|---|---|---|
| **Classification** | `claude-sonnet-4-20250514` (vision) | Identify doc type |
| **OCR** | `pytesseract` (MVP) / AWS Textract (prod) | Raw text extraction |
| **Field extraction** | Template + `claude-sonnet-4-20250514` | Structured data |
| **Cross-doc validation** | Deterministic rules | Compare across docs |

---

## 5. Pricing Agent

| Task | Model | Notes |
|---|---|---|
| **Risk-to-rate mapping** | Deterministic curve | Per loan product |
| **Term sheet generation** | `claude-haiku-4-5-20251001` | Format from structured data |
| **Scenario modeling** | Deterministic calculator | Pure math |

---

## 6. Orchestrator — No LLM Needed

Pure state machine + event routing. Entirely deterministic.

---

## Cost Estimate (~1,000 loans/month)

| Agent | Est. Cost |
|---|---|
| Sarah | ~$40 |
| Compliance | ~$15 |
| Underwriting | ~$90 |
| Document | ~$120 |
| Pricing | ~$4 |
| **Total** | **~$270/month** (~$0.27/loan) |
