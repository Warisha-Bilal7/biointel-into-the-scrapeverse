# Tanzeel's Scaffold — Deployment, Testing, Diagrams

Implements Phases 2–4 of the ops guide.

## Contents

| File/Dir | Purpose |
| --- | --- |
| `docker-compose.yml` | Orchestrates FastAPI backend + Postgres/pgvector |
| `backend/` | FastAPI app skeleton (Dockerfile, requirements, `/webhook/scrape` ingestion endpoint) |
| `backend/app/services/` | New: `drift.py` — `DriftProcessingService` class with constructor-injected `DriftEngine`; core drift analysis logic separated from endpoint |
| `mock_webhook_sender.py` | Demo-day fallback — replays saved payloads if the live scraper gets blocked |
| `payloads/` | Sample JSON payloads for the fallback script (replace with real Bright Data shape once confirmed in Phase 1) |
| `requirements-mock-sender.txt` | Python deps for the sender script (just `requests`) |
| `diagrams.md` | Component, Sequence, and State Machine diagrams (Mermaid) for Devpost/README |

## Quickstart

```bash
# 1. Bring up backend + db
docker compose up --build

# 2. Confirm it's alive
curl http://localhost:8000/health

# 3. Test ingestion locally with the fallback sender
pip install -r requirements-mock-sender.txt
python mock_webhook_sender.py --url http://localhost:8000/webhook/scrape --once payloads/sample_01.json

# 4. Check it landed
curl http://localhost:8000/events/recent
```

## What's New (Phase 3 — E2E + Architecture)

### Backend: DriftEngine deepened via constructor injection
- `_drift_engine` is now created in `lifespan` with explicit `baseline_vector` constructor parameter
- `DriftProcessingService` in `backend/app/services/drift.py` encapsulates background drift processing
- Tests use `app.dependency_overrides[DriftEngine]` to inject a mock `DriftEngine(encoder=_keyword_encode)` — no `sentence-transformers` dependency needed
- All 6 backend tests pass

### Frontend: API consumption wired
- `frontend/app/page.tsx` now fetches `GET /api/v1/scraper-health` on mount
- Drift scores, structural/semantic anomalies, and quarantined items from the backend are displayed live
- "AI DRIFT ALERT" banner shows when `is_anomalous`; "NO ALERTS" when system is healthy
- Timeline renders real events from the API, falls back to hardcoded defaults

### Three architectural deepening candidates implemented
1. **Deepen DriftEngine via Constructor Injection** — activated the existing seam; tests injectable
2. **Wire Frontend API Consumption** — dashboard now drives from backend API
3. **Extract Background Drift Processing into a Service** — `DriftProcessingService` with constructor-injected dependencies

## Next steps (remaining)

- Set `CORS_ORIGINS` env var to the live Vercel URL before deploying (Phase 2.5)
- Replace the sample payloads in `payloads/` with real captured JSON from a successful Bright Data run once the scraper is finalized (Phase 1)
- Paste the diagrams from `diagrams.md` into the Devpost submission + repo README
- Swap the in-memory `_received_events` list in `backend/app/main.py` for real SQLAlchemy models against Postgres/pgvector once Warisha's schema is ready (Phase 2 note — now using pgvector-backed `ScrapeEvent` model)
- Consider follow-up: wire `/api/v1/updates` into the timeline component (Candidate 2 extension)
- Consider follow-up: add unit tests for `DriftProcessingService` (Candidate 3 extension)

## Architecture Diagram References

- See `diagrams.md` for Mermaid component, sequence, and state machine diagrams
- Three Mermaid diagrams in the repo README/Devpost submission illustrate the 3-way handshake protocol and data flow