## Query: os.environ["DATABASE_URL"] = "sqlite:///test.db" before test imports
**Status**: ✅ WORKING — mandatory setup step
**Context**: Running backend/tests/test_backend.py pytest suite
**Error Without**: `sqlalchemy.exc.OperationalError: could not connect to server: Connection refused` (tries postgresql:// URL)
**Fix**: Single line at test file top (line 18): `os.environ["DATABASE_URL"] = "sqlite:///test.db"`
**Never Repeat**: Running `python -m pytest tests/ -q` without this env override — tests fail before executing
**Logged By**: test_backend.py line 18; all 6 tests depend on this

## Function: seed_baseline() in backend/app/main.py
**Status**: ✅ WORKING — idempotent insertion
**Context**: App lifespan event; runs on startup (Docker or local)
**Behavior**: Checks if BaselineEmbedding row exists; if not, seeds with default text + sentence-transformers vector
**Test Specific**: In tests/, DATABASE_URL=sqlite:///test.db — works with keyword fallback (_keyword_encode) since sentence-transformers may not be importable in test env
**Production**: PostgreSQL with pgvector + sentence-transformers installed — full 384-dim vector
**Never Repeat**: Manually inserting duplicate BaselineEmbedding rows — the function guards with `if existing is None`
**SQL Observation**: pgvector column type = `vector(384)`; SQLite stores as JSON list — different dtype but compatible via _keyword_encode() fallback

## Query: GET /api/v1/scraper-health DB operation
**Status**: ✅ WORKING — returns latest ScrapeEvent row
**SQL Equivalent** (from main.py:167-168):
```sql
SELECT * FROM scrape_events ORDER BY received_at DESC LIMIT 1;
```
**Returned Fields**: `last_run`, `status`, `structural_drift_score`, `semantic_drift_score`, `quarantined_items`
**Edge Case**: No events yet → returns `last_run: None, status: "idle", structural_drift_score: 0.0, semantic_drift_score: 0.0, quarantined_items: 0`
**Anomaly Logic**: `status: "anomalous"` if latest `is_anomalous == True`, else `"healthy"`
**Never Repeat**: Forgetting the `.or_()` chain for quarantined_items count (see main.py:178-182) — must filter `is_anomalous == True`

## Query: GET /api/v1/updates DB operation
**Status**: ✅ WORKING — filtered non-anomalous events
**SQL Equivalent** (from main.py:220-226):
```sql
SELECT * FROM scrape_events
WHERE is_anomalous == False
  AND structural_score IS NOT NULL
ORDER BY received_at DESC
LIMIT <limit>;
```
**Returned Confidence**: `"high"` if structural < 0.1 AND semantic < 0.15, else `"medium"`
**Key Distinction**: Unlike `/api/v1/all-events`, this ONLY returns validated (non-anomalous) events
**Never Repeat**: Confusing this with `/api/v1/all-events` — different filter (`is_anomalous == False` vs no filter)
**Index Usage**: Relies on `idx_scrape_events_received_at` index for ORDER BY performance

## Query: GET /api/v1/all-events DB operation
**Status**: ✅ WORKING — returns all events regardless of anomaly status
**SQL Equivalent** (from main.py:258-263):
```sql
SELECT * FROM scrape_events ORDER BY received_at DESC LIMIT <limit>;
```
**Includes**: Both anomalous (is_anomalous == True) and healthy events
**Admin Use**: Dashboard admin view; differs from `/api/v1/updates` which only shows non-anomalous
**Never Repeat**: Forgetting that `updates` has the `is_anomalous == False` filter that `all-events` lacks
**Recent Runs**: Both endpoints include `recent_runs` subset, but `all-events` returns full list with `is_anomalous` flag

## Operation: _process_drift() background task UPDATE
**Status**: ✅ WORKING — writes drift scores back to DB
**SQL Equivalent** (from main.py:91-93):
```sql
UPDATE scrape_events
SET structural_score = <X>,
    semantic_score = <Y>,
    is_anomalous = <True/False>,
    vector_id = <UUID or NULL>
WHERE id = <event_id>;
```
**Timing**: Runs in background after `POST /api/v1/ingest` returns 200; not immediate
**Key Logic**: If `is_anomalous == False` AND abstract exists → sets `vector_id = uuid4()`; if anomalous → vector_id stays NULL
**Never Repeat**: Calling `_process_drift()` synchronously instead of as background task — would block request/response
**Observed Issue**: If event is None (wrong event_id) → silently returns without error (line 87-88 in main.py)