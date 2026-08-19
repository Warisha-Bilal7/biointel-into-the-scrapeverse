# biointel-into-the-scrapeverse — Agent Quickstart

## Project Structure

```
biointel-into-the-scrapeverse/
├── backend/              # Warisha's FastAPI + PostgreSQL/pgvector
│   ├── app/main.py       # Entrypoint: POST /api/v1/ingest, GET /api/v1/scraper-health
│   ├── tests/test_backend.py  # 6 pytest tests (structural drift, semantic drift, API)
│   └── mock_webhook_sender.py # Fallback script if scraper gets blocked
├── mock_webhook_sender.py # Person C fallback: blast pre-saved payloads to backend
├── Person_A_Backend_Guide.md  # Warisha's guide (for reference only)
├── Person_B_Arsh_Frontend_Guide.md  # Arsh's guide (for reference only)
├── Person_C_Tanzeel_Ops_Guide.md  # Execution plan & status
├── README.md             # Project overview + 3 Mermaid diagrams
├── TDD-sheet.md          # API contract & drift thresholds (single source of truth)
└── Integration_Guide.md  # 3-way handshake protocol
```

## Essential Commands

| Action | Command |
|---|---|
| Run all backend tests | `cd backend && python -m pytest tests/ -q` |
| Verify backend endpoints | `python -c "from fastapi.testclient import TestClient; from app.main import app; client = TestClient(app); ..."` |
| Run mock webhook sender | `python mock_webhook_sender.py http://localhost:8000/api/v1/ingest` |
| Start backend locally | `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000` |

## API Contract (TDD-sheet.md)

**Single source of truth** — if keys change, all three members must sync.

- Scraper → Backend: `POST /api/v1/ingest`
  - Payload: `{source_url, title, abstract, status, timestamp}`
- Backend → Frontend: `GET /api/v1/scraper-health`
  - Response: `{last_run, status, structural_drift_score, semantic_drift_score, quarantined_items}`
- Drift thresholds: semantic > 0.35 or structural > 0.20 → `is_anomalous = True`

## Key Conventions

- **CORS**: Backend currently allows `["*"]` — update with Vercel frontend URL before production (Phase 2.5)
- **Drift math**: `calculate_structural_drift(payload)` checks expected keys: `source_url, title, abstract, status, timestamp`
- **Semantic drift**: `calculate_semantic_drift(text, baseline_vector)` — uses sentence-transformers if available, falls back to keyword matching
- **Test prerequisites**: All 6 tests must pass before E2E validation (Phase 3)
- **Fallback**: `mock_webhook_sender.py` provides pre-saved payloads if scraper is blocked during judging

## Phase Status (from ops guide)

| Phase | Status | Notes |
|---|---|---|
| 1 — Bright Data Extraction | ✅ Complete | Scraper Studio + webhook configured; DOM targets from Arsh needed |
| 2 — Cloud Deployment | ✅ Complete | Backend + frontend deployed; CORS verified |
| 3 — E2E Testing | ✅ Complete | Live demo works; mock_webhook_sender.py tested |
| 4 — Diagrams + Pitch | ✅ Complete | 3 Mermaid diagrams in README/Devpost |

## What NOT to do

- Don't restructure `backend/app/` — the `main.py` entrypoints and test imports are wired for this layout
- Don't change drift threshold values (0.20 structural, 0.35 semantic) without updating TDD-sheet.md and all 3 test assertions
- Don't forget to update CORS `allow_origins` when deploying to Vercel production