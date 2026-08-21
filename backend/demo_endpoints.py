import os, json, sys

os.environ["DATABASE_URL"] = "sqlite:///test_demo.db"
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from app.database import Base, engine, SessionLocal
from app.models import BaselineEmbedding
from app.drift import _encode

Base.metadata.create_all(bind=engine)

sess = SessionLocal()
if not sess.query(BaselineEmbedding).first():
    vec = _encode(
        "Clinical trial evaluating efficacy and safety of therapeutic intervention "
        "in patients with disease. Randomized controlled study with primary endpoint "
        "of treatment outcome. Phase study enrolling participants across clinical "
        "sites. Investigational drug therapy for medical condition. Patient outcomes "
        "and adverse events being monitored in this clinical research study."
    )
    sess.add(BaselineEmbedding(label="default", embedding_json=json.dumps(vec)))
    sess.commit()
sess.close()

from fastapi.testclient import TestClient
from app.main import app
c = TestClient(app)

print("=" * 60)
print("1. GET /health")
print("=" * 60)
print(json.dumps(c.get("/health").json(), indent=2))

print("\n" + "=" * 60)
print("2. POST /api/v1/ingest  (valid clinical trial)")
print("=" * 60)
print(json.dumps(c.post("/api/v1/ingest", json={
    "source_url": "https://clinicaltrials.gov/study/NCT05901234",
    "title": "Phase 3 Randomized Trial of Pembrolizumab in Metastatic NSCLC",
    "abstract": (
        "This phase 3 double-blind randomized placebo-controlled trial evaluates "
        "the efficacy and safety of pembrolizumab in combination with platinum-based "
        "chemotherapy in participants with previously untreated metastatic non-small "
        "cell lung cancer whose tumors express PD-L1. Primary endpoint is overall survival. "
        "Secondary endpoints include progression-free survival and objective response rate."
    ),
    "status": "Recruiting",
    "timestamp": "2026-08-20T08:00:00Z"
}).json(), indent=2))

print("\n" + "=" * 60)
print("3. POST /api/v1/ingest  (anomalous garbage payload)")
print("=" * 60)
print(json.dumps(c.post("/api/v1/ingest", json={
    "source_url": "https://clinicaltrials.gov/study/NCT05901234",
    "title": "",
    "abstract": (
        "Click here to accept cookies. Terms of service apply. "
        "Copyright 2026 Website Inc. All rights reserved."
    ),
    "status": "",
    "timestamp": "2026-08-20T10:00:00Z"
}).json(), indent=2))

print("\n" + "=" * 60)
print("4. POST /api/v1/ingest  (protocol drift - endpoint changed)")
print("=" * 60)
print(json.dumps(c.post("/api/v1/ingest", json={
    "source_url": "https://clinicaltrials.gov/study/NCT05901234",
    "title": "Phase 3 Trial of Pembrolizumab in NSCLC",
    "abstract": (
        "This study evaluates pembrolizumab with chemotherapy in patients with "
        "metastatic non-small cell lung cancer. Primary endpoint has been revised "
        "from progression-free survival to overall survival as of protocol amendment v3.0. "
        "Study status updated to active, not recruiting pending safety review."
    ),
    "status": "Active, not recruiting",
    "timestamp": "2026-08-20T10:30:00Z"
}).json(), indent=2))

# Wait for background tasks to finish
import time; time.sleep(3)

print("\n" + "=" * 60)
print("5. GET /api/v1/scraper-health")
print("=" * 60)
print(json.dumps(c.get("/api/v1/scraper-health").json(), indent=2))

print("\n" + "=" * 60)
print("6. GET /api/v1/updates")
print("=" * 60)
print(json.dumps(c.get("/api/v1/updates").json(), indent=2))

print("\n" + "=" * 60)
print("7. GET /api/v1/all-events")
print("=" * 60)
print(json.dumps(c.get("/api/v1/all-events").json(), indent=2))
