"""
Backend tests for BioIntel Guardian.

6 tests covering:
  1. Structural drift: valid payload -> low score
  2. Structural drift: missing keys -> high score -> is_anomalous
  3. Semantic drift: similar biomedical text vs baseline -> low score
  4. Semantic drift: garbage/website footer vs baseline -> high score -> is_anomalous
  5. API POST /api/v1/ingest returns 200 + event_id
  6. API GET /api/v1/scraper-health returns correct shape
"""

import os
import sys
import json as _json

# Force SQLite before any app imports
os.environ["DATABASE_URL"] = "sqlite:///test.db"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.drift import (
    calculate_structural_drift,
    calculate_semantic_drift,
    analyze_payload,
    _encode,
    STRUCTURAL_THRESHOLD,
    SEMANTIC_THRESHOLD,
)

from sqlalchemy import create_engine, event
from app.database import Base, engine, SessionLocal
from app.models import ScrapeEvent, BaselineEmbedding
from datetime import datetime

# Remove any stale test DB
if os.path.exists("test.db"):
    os.remove("test.db")

# Create all tables on the test engine
Base.metadata.create_all(bind=engine)

# Enable WAL mode and foreign keys for SQLite
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Seed a baseline embedding for tests
_session = SessionLocal()
_existing = _session.query(BaselineEmbedding).first()
if _existing is None:
    _baseline_text = (
        "Phase 3 randomized double-blind placebo-controlled trial evaluating "
        "efficacy and safety of drug intervention in patients with chronic condition. "
        "Primary endpoint is reduction in disease severity score. "
        "Study is currently recruiting participants across multiple clinical sites."
    )
    _vec = _encode(_baseline_text)
    _emb = BaselineEmbedding(label="default", embedding_json=_json.dumps(_vec))
    _session.add(_emb)
    _session.commit()
_session.close()

from fastapi.testclient import TestClient
from app.main import app


# ---------------------------------------------------------------------------
# 1. Structural drift — valid payload
# ---------------------------------------------------------------------------

def test_structural_drift_valid_payload():
    payload = {
        "source_url": "https://clinicaltrials.gov/ct2/show/NCT05000001",
        "title": "Phase 3 Trial of Drug X",
        "abstract": "A randomized controlled trial evaluating Drug X.",
        "status": "Recruiting",
        "timestamp": "2026-08-18T20:00:00Z",
    }
    score = calculate_structural_drift(payload)
    assert score <= STRUCTURAL_THRESHOLD, (
        f"Valid payload should have structural drift <= {STRUCTURAL_THRESHOLD}, got {score}"
    )


# ---------------------------------------------------------------------------
# 2. Structural drift — missing keys -> anomalous
# ---------------------------------------------------------------------------

def test_structural_drift_missing_keys_anomalous():
    payload = {"source_url": "https://example.com"}
    score = calculate_structural_drift(payload)
    assert score > STRUCTURAL_THRESHOLD, (
        f"Payload missing 4 keys should exceed threshold {STRUCTURAL_THRESHOLD}, got {score}"
    )

    full_result = analyze_payload({"source_url": "https://example.com"})
    assert full_result["is_anomalous"] is True, "Should flag as anomalous when structural drift is high"


# ---------------------------------------------------------------------------
# 3. Semantic drift — similar biomedical text
# ---------------------------------------------------------------------------

def test_semantic_drift_similar_text():
    baseline_text = (
        "Phase 3 randomized double-blind placebo-controlled trial evaluating "
        "efficacy and safety of drug intervention in patients with chronic condition. "
        "Primary endpoint is reduction in disease severity score. "
        "Study is currently recruiting participants across multiple clinical sites."
    )
    baseline_vec = _encode(baseline_text)
    new_text = (
        "A phase 3 double-blind study assessing the safety and efficacy of a new drug "
        "in patients with the same chronic condition. The primary endpoint measures "
        "disease severity reduction."
    )
    score = calculate_semantic_drift(new_text, baseline_vec)
    assert score <= SEMANTIC_THRESHOLD, (
        f"Similar biomedical text should be within threshold {SEMANTIC_THRESHOLD}, got {score}"
    )


# ---------------------------------------------------------------------------
# 4. Semantic drift — garbage / website footer -> anomalous
# ---------------------------------------------------------------------------

def test_semantic_drift_garbage_text_anomalous():
    baseline_text = (
        "Phase 3 randomized double-blind placebo-controlled trial evaluating "
        "efficacy and safety of drug intervention in patients with chronic condition. "
        "Primary endpoint is reduction in disease severity score."
    )
    baseline_vec = _encode(baseline_text)
    garbage_text = (
        "Click here to accept cookies. Terms of service apply. "
        "Copyright 2026 Website Inc. All rights reserved. "
        "Follow us on Twitter. Privacy policy."
    )
    score = calculate_semantic_drift(garbage_text, baseline_vec)
    assert score > SEMANTIC_THRESHOLD, (
        f"Garbage text should exceed semantic threshold {SEMANTIC_THRESHOLD}, got {score}"
    )

    full_result = analyze_payload({
        "source_url": "https://example.com",
        "title": "Footer Content",
        "abstract": garbage_text,
        "status": "Unknown",
        "timestamp": "2026-08-18T20:00:00Z",
    })
    assert full_result["is_anomalous"] is True, "Garbage abstract should be flagged as anomalous"


# ---------------------------------------------------------------------------
# 5. API POST /api/v1/ingest
# ---------------------------------------------------------------------------

def test_api_ingest():
    client = TestClient(app)

    payload = {
        "source_url": "https://clinicaltrials.gov/ct2/show/NCT05000001",
        "title": "Phase 3 Trial of Drug X",
        "abstract": "A randomized controlled trial evaluating Drug X in patients.",
        "status": "Recruiting",
        "timestamp": "2026-08-18T20:00:00Z",
    }
    resp = client.post("/api/v1/ingest", json=payload)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    body = resp.json()
    assert body["status"] == "received"
    assert "event_id" in body


# ---------------------------------------------------------------------------
# 6. API GET /api/v1/scraper-health
# ---------------------------------------------------------------------------

def test_api_scraper_health():
    client = TestClient(app)

    resp = client.get("/api/v1/scraper-health")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    body = resp.json()
    assert "last_run" in body
    assert "status" in body
    assert "structural_drift_score" in body
    assert "semantic_drift_score" in body
    assert "quarantined_items" in body
