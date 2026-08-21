---
name: biointel-drift-ops
description: Implementation log and anti-pattern library for the biointel-into-the-scrapeverse clinical trial drift monitoring project
---

# biointel-drift-ops Skill

**Skill ID**: `biointel-drift-ops`  
**Description**: Implementation log and anti-pattern library for the `biointel-into-the-scrapeverse` project — a 3-part system (Scraper → Backend → Frontend) for monitoring clinical trial data drift with AI.

## Installation

```bash
# Project-level install (within the project directory):
npx skills add biointel-drift-ops

# Or use the local path reference:
export SKILL_PATH="./biointel-drift-ops"
```

## Project Overview

This skill encapsulates the hard-won implementation knowledge from the `biointel-into-the-scrapeverse` project, where three team members (Tanzeel/Warisha/Arsh) built a clinical trial drift monitoring system. All 4 phases are complete:

- **Phase 1**: Bright Data extraction + webhook → FastAPI backend
- **Phase 2**: Dockerization + cloud deployment + CORS
- **Phase 3**: E2E testing + mock_webhook_sender.py fallback
- **Phase 4**: Diagrams + pitch assets

---

## Three Logger Files (Core This Skill)

This skill's primary value is centralizing the implementation knowledge from three project logger files, preventing agents from repeating failed approaches.

### 1. `bashlog.md` — Bash Command Log & Warnings

**Purpose**: Track bash commands that failed, produced errors, or caused issues. Each entry flags the command so agents avoid reusing it, preventing token garbage from repeated troubleshooting.

**Entry Format**:
```
## Command: <exact command string>
**Status**: ❌ FAILED / ⚠️ WARNING / ✅ OK / 🔧 FIXED
**Directory**: <working directory path>
**Error Type**: <syntax error / import failure / port conflict / timeout>
**Why It Failed**: <root cause analysis>
**Do Not Reuse Because**: <specific anti-pattern prevention>
**Current Status**: <still broken / fixed in commit X / pending>
```

**Logged Commands (5 entries)**:

1. **`docker compose up --build`** — Port 8000 already in use from previous session; always check `docker ps` first
2. **`python -m pytest tests/ -q`** (without DATABASE_URL override) — Fails with connection refused; must set `os.environ["DATABASE_URL"] = "sqlite:///test.db"` first
3. **`python mock_webhook_sender.py --url http://localhost:8000/webhook/scrape`** — 404 because route is `/api/v1/ingest`, not `/webhook/scrape`
4. **`from sentence_transformers import SentenceTransformer` at module level** — Cold start failure in Docker slim image; use `_get_model()` lazy-initialization pattern instead
5. **`from app.main import app`** (in tests without DATABASE_URL) — Tests crash before executing; always override DATABASE_URL before test imports

**Usage Rule**: Before running any bash command referenced in this file, check `bashlog.md` first and skip/modify accordingly.

---

### 2. `payload.md` — Payload Contract & Samples

**Purpose**: Single source of truth for API payload structure, sample data, and drift-triggering conditions. All three team members must sync on any key changes.

**Payload Contract** (from TDD-sheet.md):
```json
{
  "source_url": "https://...",
  "title": "Phase 3 Trial...",
  "abstract": "The study evaluates...",
  "status": "Recruiting",
  "timestamp": "2026-08-18T20:00:00Z"
}
```

**Expected Keys**: `source_url`, `title`, `abstract`, `status`, `timestamp`

**Drift Thresholds**:
- Structural > 0.20 → `is_anomalous = True`
- Semantic > 0.35 → `is_anomalous = True`

**Sample Payloads** (in `payloads/`):

| Filename | Description | Drift Behavior |
|---|---|---|
| `sample_01.json` | Valid trial data (Recruiting) | structural=0.0, semantic≈0.0, is_anomalous=False |
| `sample_02_protocol_drift.json` | Protocol amendment (status change) | structural=0.0, semantic varies, is_anomalous depends on abstract |
| `sample_03_anomalous.json` | Empty title + cookie-policy abstract | structural=0.8 (missing keys), semantic>0.35, is_anomalous=True |

**Mock Webhook Sender Usage**:
```
python mock_webhook_sender.py --once payloads/sample_01.json
python mock_webhook_sender.py --url http://localhost:8000/api/v1/ingest --loop
```

**Update Policy**: If any payload key changes, update `TDD-sheet.md` and all 6 test assertions.

---

### 3. `dblog.md` — Database Schema & Query Log

**Purpose**: Document the PostgreSQL/pgvector schema, table structures, and key queries used by the FastAPI backend. Helps agents debug data persistence and drift storage.

**Schema** (`db/init/01_schema.sql`):
- `pgvector` extension enabled
- `scrape_events` table: `id`, `source_url`, `title`, `abstract`, `status`, `timestamp`, `received_at`, `structural_score`, `semantic_score`, `is_anomalous`, `vector_id`, `raw_payload`, `created_at`
- `baseline_embeddings` table: `id`, `label`, `embedding vector(384)`, `created_at`
- Indexes: `idx_scrape_events_received_at`, `idx_scrape_events_is_anomalous`, `idx_baseline_embeddings_label`

**Key Tables & Columns**:

| Table | Key Columns |
|---|---|
| `scrape_events` | `id`, `source_url`, `structural_score`, `semantic_score`, `is_anomalous`, `received_at` |
| `baseline_embeddings` | `label`, `embedding` (vector(384)) |

**Key Queries** (from `main.py`):

| Endpoint | Purpose | Key SQL |
|---|---|---|
| `GET /health` | Hardcoded health response | `SELECT {...}` (hardcoded) |
| `POST /api/v1/ingest` | INSERT + background drift task | INSERT into `scrape_events` + background task |
| `GET /api/v1/scraper-health` | Latest event + anomaly count | `SELECT * FROM scrape_events ORDER BY received_at DESC LIMIT 1` |
| `GET /api/v1/updates` | Non-anomalous events only | `WHERE is_anomalous == False AND structural_score IS NOT NULL` |
| `GET /api/v1/all-events` | All events unfiltered | `ORDER BY received_at DESC LIMIT N` |

**Drift Storage Flow**:
```
ingest → ScrapeEvent row created → _process_drift() background task →
analyze_payload() → calculate_structural_drift + calculate_semantic_drift →
UPDATE structural_score, semantic_score, is_anomalous, vector_id
```

**Baseline Seeding**:
- `seed_baseline()` in `main.py` only inserts if no existing `BaselineEmbedding`
- Text: "Phase 3 randomized double-blind placebo-controlled trial..."
- Vector: `all-MiniLM-L6-v2` (384-dim) via sentence-transformers or keyword fallback

**Note**: SQLite used for testing (`DATABASE_URL=sqlite:///test.db`); production uses PostgreSQL with pgvector.

---

## Anti-Patterns (Never Repeat)

### Bash Commands

| Command | Why It Fails | Alternative |
|---|---|---|
| `docker compose up --build` (cold start) | Port 8000 occupied; Docker not running | `docker compose down && docker compose up --build` |
| `python -m pytest tests/ -q` (no env override) | Database connection refused | `os.environ["DATABASE_URL"] = "sqlite:///test.db"` first |
| `python mock_webhook_sender.py --url .../webhook/scrape` | 404 — wrong route | Use `--url http://localhost:8000/api/v1/ingest` |
| `from sentence_transformers import ...` at module level | Cold start / timeout | Use `_get_model()` with try/except fallback |
| pytest imports without `DATABASE_URL` override | Runtime errors | Set env var on line 18 of test files |

### Payload Patterns

| Anti-Pattern | Consequence | Correct Approach |
|---|---|---|
| Omitting any of 5 expected keys | Structural drift > 0.20 → anomalous | Always include: source_url, title, abstract, status, timestamp |
| Using cookie-policy text as "valid" abstract | Semantic drift > 0.35 → anomalous (intended for test only) | Reserve `sample_03_anomalous.json` for anomaly testing only |
| Assuming status change affects structural drift | Misunderstanding — only keys matter | Structural drift depends on key presence/absence, not values |
| Mock sender without `--url` flag | Interactive prompt / failure | Always provide `--url` argument |

### Database Anti-Patterns

| Anti-Pattern | Consequence | Fix |
|---|---|---|
| Running pytest without `DATABASE_URL=sqlite:///test.db` | Tests fail before executing | Always override DATABASE_URL first |
| Confusing `/api/v1/updates` with `/api/v1/all-events` | Different filters (`is_anomalous == False` vs none) | Remember: `updates` only shows non-anomalous events |
| Manual duplicate `BaselineEmbedding` insertion | Guarded by `if existing is None` | Let `seed_baseline()` handle seeding; don't manually insert |
| Calling `_process_drift()` synchronously | Blocks request/response | Always use background tasks; let FastAPI manage async |
| Forgetting pgvector `vector(384)` dtype in SQLite | Compatible via `_keyword_encode()` fallback | Accept different storage; fallback works |

---

## Best Practices (Documented Workflows)

### 1. Test Execution

```bash
# Always: set DATABASE_URL first, then run pytest
os.environ["DATABASE_URL"] = "sqlite:///test.db"
python -m pytest tests/ -q
```

### 2. Docker Development

```bash
# Safe compose up sequence
docker compose down
# Verify nothing on port 8000: docker ps -a | grep 8000
docker compose up --build
```

### 3. Webhook Sender

```bash
# Single payload (recommended for E2E validation)
python mock_webhook_sender.py --once payloads/sample_01.json

# Loop mode (demo-day fallback)
python mock_webhook_sender.py --url http://localhost:8000/api/v1/ingest --loop
```

### 4. Payload Design

- **Valid payload**: All 5 keys present → structural drift = 0.0
- **Anomaly trigger**: Missing keys → structural > 0.20; garbage abstract → semantic > 0.35
- **Protocol drift**: Status change alone doesn't trigger structural drift; abstract content affects semantic drift
- **Always validate**: Use `calculate_structural_drift()` and `calculate_semantic_drift()` before waypoint commits

### 4. Database Operations

- `seed_baseline()` is idempotent — never manually insert BaselineEmbedding rows
- `scraper-health` returns `"idle"` status when no events exist
- `updates` endpoint filters `is_anomalous == False`; `all-events` has no such filter
- Drift scores are written by `_process_drift()` in background, not immediately

---

## Skill Ecosystem Integration

**Discovery**: This skill can be found via the Skills CLI:

```bash
# Search related queries
npx skills find fastapi        # API framework
npx skills find pytest         # testing  
npx skills find docker         # containerization
npx skills find pgvector       # vector database
npx skills find mermaid        # diagrams
```

**Installation**: Once published to the ecosystem, install with:

```bash
npx skills add biointel-drift-ops
# Or use local path:
export SKILL_PATH="$HOME/.agents/skills/biointel-drift-ops"
# Or project-level:
export SKILL_PATH="./biointel-drift-ops"
```

**Related Skills**: Skills that complement this one:

| Skill | Why It Helps |
|---|---|
| `vercel-labs/agent-skills` | React/Next.js frontend patterns; CORS configuration |
| `anthropics/skills` | Document processing; abstract text analysis |
| `ComposioHQ/awesome-claude-skills` | Workflow automation; test automation |
| Custom skill: `drift-detection-engine` | Reusable drift calculation pipeline (sentence-transformers + pgvector) |

---

## Version & Maintenance

**Version**: 1.0.0 (initial release — all 4 phases complete)  
**Last Updated**: 2026-08-20  
**Maintainers**: Project team (Tanzeel/Warisha/Arsh)  
**Compatibility**: Requires Python 3.11+, FastAPI, SQLAlchemy, pgvector, sentence-transformers  

**Changelog**: 
- `1.0.0` — Initial release with 3 logger files documented (bashlog.md, payload.md, dblog.md)
- All 6 existing backend tests verified passing
- Anti-patterns documented from implementation experience

**Contributing**: Add new anti-pattern entries as the project evolves. Update thresholds if drift values change (currently: structural > 0.20, semantic > 0.35 per TDD-sheet.md).

---

## Quick Reference Cheat Sheet

### Before Any Operation:

```
✓ Check bashlog.md    — Avoid failed bash commands
✓ Check payload.md    — Validate payload structure
✓ Check dblog.md      — Verify DB query patterns
✓ Set DATABASE_URL    — sqlite:///test.db for tests
✓ Run: pytest -q     — All 6 tests must pass
```

### Key Thresholds (TDD-sheet.md):

```
Structural drift > 0.20 → is_anomalous = True
Semantic drift   > 0.35 → is_anomalous = True
```

### Endpoint Quick Routes:

```
GET    /api/v1/ingest      — POST payload (drift runs in background)
GET    /api/v1/scraper-health  — Latest drift telemetry
GET    /api/v1/updates     — Non-anomalous validated events
GET    /api/v1/all-events  — All events (admin view)
GET    /health             — Service health check
```

---
*This skill is part of the biointel-into-the-scrapeverse project ecosystem. For the full project structure, see README.md and TDD-sheet.md.*