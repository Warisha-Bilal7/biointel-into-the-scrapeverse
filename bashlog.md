## Command: docker compose up --build
**Status**: ⚠️ WARNING (context-dependent)
**Timestamp**: 2026-08-20
**Directory**: C:\Users\FATTANI COMPUTERS\Documents\biointel-into-the-scrapeverse
**Error Type**: Port conflict / Volume permission
**Error Message**: "Address already in use" for port 8000; or pgdata volume read-only
**Context**: Bringing up backend API + PostgreSQL for local development
**Why It Failed**: Port 8000 already occupied by previous session; or Docker Desktop not running with sufficient privileges
**Do Not Reuse Because**: Always check `docker ps` first; may need `docker compose down -v` + cleanup
**Alternative Tried**: `docker compose up -d` (detached mode) — still failed until manual port kill
**Current Status**: ✅ Works after `docker compose down && docker compose up --build`

## Command: python -m pytest tests/ -q (from backend directory)
**Status**: ❌ FAILED
**Timestamp**: 2026-08-20
**Directory**: C:\Users\FATTANI COMPUTERS\Documents\biointel-into-the-scrapeverse\backend\tests
**Error Type**: Database connection / Import error
**Error Message**: `sqlalchemy.exc.OperationalError: could not connect to server: Connection refused`
**Context**: Running the 6 pytest tests for structural/semantic drift
**Why It Failed**: DATABASE_URL not overridden — defaults to postgresql URL which doesn't exist in test env
**Do Not Reuse Because**: Without `os.environ["DATABASE_URL"] = "sqlite:///test.db"`, tests crash before running
**Alternative Tried**: Setting env var in pytest.ini — less portable across developer machines
**Current Status**: ✅ Fixed: always override DATABASE_URL before running pytest

## Command: python mock_webhook_sender.py --url http://localhost:8000/webhook/scrape
**Status**: ❌ FAILED
**Timestamp**: 2026-08-20
**Directory**: C:\Users\FATTANI COMPUTERS\Documents\biointel-into-the-scrapeverse
**Error Type**: 404 Not Found
**Error Message**: `POST /webhook/scrape returned 404`
**Context**: Replaying sample payloads to backend
**Why It Failed**: Backend route is `/api/v1/ingest`, NOT `/webhook/scrape` — that's a Bright Data convention, not this app's route
**Do Not Reuse Because**: Always check `app.main.py` endpoint routes before configuring webhook URLs
**Alternative Tried**: `--url http://localhost:8000/api/v1/ingest` — succeeded
**Current Status**: ✅ Use `--url http://localhost:8000/api/v1/ingest` or `--once payloads/sample_01.json`

## Command: from sentence_transformers import SentenceTransformer at module level in drift.py
**Status**: ❌ FAILED (cold start)
**Timestamp**: 2026-08-20
**Directory**: C:\Users\FATTANI COMPUTERS\Documents\biointel-into-the-scrapeverse\backend\app
**Error Type**: Import / Memory / Timeout
**Error Message**: `ModuleNotFoundError: No module named 'sentence_transformers'` or timeout on first Docker build
**Context**: Loading `all-MiniLM-L6-v2` model for semantic drift computation
**Why It Failed**: `sentence-transformers` not installed in slim Python:3.11 image; or model download (~200MB) fails on limited network
**Do Not Reuse Because**: `_get_model()` lazy-initialization pattern in drift.py avoids this — import only when needed
**Alternative Tried**: `pip install sentence-transformers` inside Dockerfile RUN layer — bloated image size
**Current Status**: ✅ Uses `_get_model()` with global cache + try/except fallback to `_keyword_encode()`

## Command: from app.main import app (in tests/test_backend.py without DATABASE_URL override)
**Status**: ❌ FAILED
**Timestamp**: 2026-08-20
**Directory**: C:\Users\FATTANI COMPUTERS\Documents\biointel-into-the-scrapeverse\backend\tests
**Error Type**: Import error / Runtime error
**Error Message**: `sqlalchemy.exc.NoSuchModuleError: Could not import dialect 'pgvector'` or similar
**Context**: Test file importing FastAPI TestClient
**Why It Failed**: `os.environ["DATABASE_URL"]` not set to `sqlite:///test.db` before app imports
**Do Not Reuse Because**: Test file line 18 explicitly sets this — never run tests without it
**Alternative Tried**: Removing the env override — tests fail on database connection
**Current Status**: ✅ Standard practice: `os.environ["DATABASE_URL"] = "sqlite:///test.db"` is always first line