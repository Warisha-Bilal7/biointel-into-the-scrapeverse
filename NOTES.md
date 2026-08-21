# Domain Notes — BioIntel Guardian

## Personas / Roles
- **Warisha (Backend)**: FastAPI + PostgreSQL/pgvector, drift detection, ingestion API
- **Arsh (Frontend)**: Next.js UI on Vercel, consumes `/api/v1/scraper-health`
- **Tanzeel (Ops)**: Orchestration, ops guide, mock webhook sender, E2E testing

## Core API Contract (TDD-sheet.md — single source of truth)

### Scraper → Backend: POST /api/v1/ingest
JSON payload with these 5 keys:
- `source_url` (e.g. "https://clinicaltrials.gov/ct2/show/NCT05000001")
- `title` (e.g. "Phase 3 Trial of Drug X")
- `abstract` (e.g. "A randomized controlled trial evaluating Drug X.")
- `status` (e.g. "Recruiting")
- `timestamp` (e.g. "2026-08-18T20:00:00Z")

### Backend → Frontend: GET /api/v1/scraper-health
Response with drift telemetry:
- `last_run` (ISO timestamp or null)
- `status` ("anomalous" or "healthy")
- `structural_drift_score` (float, 0–1)
- `semantic_drift_score` (float, 0–1)
- `quarantined_items` (count of anomalous events)

## Drift Math (For pytest suite)

**Structural Drift (D_str)**: Missing / extra keys vs expected schema → score [0, 1]
- Expected keys: `source_url, title, abstract, status, timestamp`
- Threshold: `structural > 0.20` → `is_anomalous == True`

**Semantic Drift (D_sem)**: Cosine distance between incoming text vector and baseline vector
- Test constraint: `D_sem > 0.35` → `is_anomalous == True`
- Uses `sentence-transformers all-MiniLM-L6-v2` if available, falls back to keyword matching

## Key Values
- `STRUCTURAL_THRESHOLD = 0.20`
- `SEMANTIC_THRESHOLD = 0.35`

## Models (backend/app/models.py)
- **ScrapeEvent**: id (UUID text PK), source_url, title, abstract, status, timestamp, received_at, structural_score, semantic_score, is_anomalous, vector_id, raw_payload, created_at
- **BaselineEmbedding**: id (UUID text PK), label ("default"), embedding_json (text), created_at; has `.embedding` property that loads/serialises the vector

## Drift Engine (backend/app/drift.py)
- `calculate_structural_drift(payload)` → float in [0,1]
- `calculate_semantic_drift(text, baseline_vector)` → float in [0,1]
- `analyze_payload(payload)` → {structural_score, semantic_score, is_anomalous}
- `_encode(text)` → list[float] (sentence-transformers model lazy-load, keyword fallback)
- `_get_model()` → loads `SentenceTransformer("all-MiniLM-L6-v2")` globally, or sets `_model = False`

## Drip Detection Edge Cases (recent bug fix)
- Keys with empty/None values (e.g. `"title": ""`, `"status": ""`) are now treated as missing data for structural drift calculation
- Payload `sample_03_anomalous.json` (4-of-5 keys present, title="" and status="", timestamp missing) now correctly flags `is_anomalous = True` (drift 0.6 > 0.20)

## CORS
- Backend allows `["*"]` in development; update with Vercel frontend URL before production (Phase 2.5)

## Test Suite (6 pytest tests, backend/tests/test_backend.py)
1. `test_structural_drift_valid_payload` — valid 5-key payload → structural drift ≤ 0.20
2. `test_structural_drift_missing_keys_anomalous` — 1 key present → structural drift > 0.20 → is_anomalous
3. `test_semantic_drift_similar_text` — biomedical abstract similar to baseline → semantic score ≤ 0.35
4. `test_semantic_drift_garbage_text_anomalous` — cookie policy / website footer → semantic score > 0.35 → is_anomalous
5. `test_api_ingest` — POST /api/v1/ingest returns 200 + event_id
6. `test_api_scraper_health` — GET /api/v1/scraper-health returns correct shape

## Phase Status (from ops guide)
| Phase | Status | Notes |
|---|---|---|
| 1 — Bright Data Extraction | ✅ Complete | Scraper Studio + webhook configured; DOM targets from Arsh needed |
| 2 — Cloud Deployment | ✅ Complete | Backend + frontend deployed; CORS verified |
| 3 — E2E Testing | ✅ Complete | Live demo works; mock_webhook_sender.py tested |
| 4 — Diagrams + Pitch | ✅ Complete | 3 Mermaid diagrams in README/Devpost |

## Recent fixes
- **Structural drift bug (Aug 2026)**: Keys with empty string values were not counted as missing, causing payloads like `sample_03_anomalous.json` to fall through the anomaly threshold. Fixed by treating `not payload[key]` as missing in `calculate_structural_drift()`.