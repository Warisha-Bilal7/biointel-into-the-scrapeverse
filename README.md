# Tanzeel's Scaffold — Deployment, Testing, Diagrams

Implements Phases 2–4 of the ops guide.

## Contents

| File/Dir | Purpose |
|---|---|
| `docker-compose.yml` | Orchestrates FastAPI backend + Postgres/pgvector |
| `backend/` | FastAPI app skeleton (Dockerfile, requirements, `/webhook/scrape` ingestion endpoint) |
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

## Next steps (not yet wired)

- Swap the in-memory `_received_events` list in `backend/app/main.py` for real
  SQLAlchemy models against Postgres/pgvector once Warisha's schema is ready.
- Point Bright Data's webhook delivery action at `/webhook/scrape` on the
  deployed backend URL (Phase 2.4).
- Set `CORS_ORIGINS` env var to the live Vercel URL before deploying (Phase 2.5).
- Replace the sample payloads in `payloads/` with real captured JSON from a
  successful Bright Data run once the scraper is finalized (Phase 1).
- Paste the diagrams from `diagrams.md` into the Devpost submission + repo README.
