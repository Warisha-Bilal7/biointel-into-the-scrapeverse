import os
import uuid
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from .database import engine, SessionLocal, Base
from .models import ScrapeEvent, BaselineEmbedding
from .drift_adapter import DriftEngine
from .services.drift import DriftProcessingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global drift engine instance — real dependencies for production use.
# Tests can replace it with a DriftEngine injected with mock encoder/baseline
# via FastAPI dependency_oververs.
_drift_engine: Optional[DriftEngine] = DriftEngine()


def init_db():
    Base.metadata.create_all(bind=engine)


def seed_baseline():
    db = SessionLocal()
    try:
        existing = db.query(BaselineEmbedding).first()
        if existing is None:
            baseline_text = (
                "Clinical trial evaluating efficacy and safety of therapeutic intervention "
                "in patients with disease. Randomized controlled study with primary endpoint "
                "of treatment outcome. Phase study enrolling participants across clinical "
                "sites. Investigational drug therapy for medical condition. Patient outcomes "
                "and adverse events being monitored in this clinical research study."
            )
            vec = _encode(baseline_text)
            emb = BaselineEmbedding(label="default", embedding=vec)
            db.add(emb)
            db.commit()
            logger.info("Seeded baseline embedding for drift detection")
    except Exception as e:
        logger.warning("Could not seed baseline embedding: %s", e)
        db.rollback()
    finally:
        db.close()


def _make_drift_engine() -> DriftEngine:
    """Create a DriftEngine instance with real dependencies (model + baseline)."""
    # The baseline vector is computed from the seeded text; in production this
    # would come from the DB, but for the minimal refactor we compute it here
    # and pass it to the constructor so the dependency is explicit.
    baseline_text = (
        "Clinical trial evaluating efficacy and safety of therapeutic intervention "
        "in patients with disease. Randomized controlled study with primary endpoint "
        "of treatment outcome. Phase study enrolling participants across clinical "
        "sites. Investigational drug therapy for medical condition. Patient outcomes "
        "and adverse events being monitored in this clinical research study."
    )
    baseline_vec = _encode(baseline_text)
    return DriftEngine(baseline_vector=baseline_vec)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Create the drift engine once per worker process; its dependencies are
    # explicit (encoder, baseline_vector) so the seam is real, not hidden.
    global _drift_engine
    _drift_engine = _make_drift_engine()
    # Create the processing service with the injected engine; this makes the
    # background drift processing testable via a mock DriftEngine.
    from fastapi import BackgroundTasks
    app.state.drift_service = DriftProcessingService(_drift_engine)
    seed_baseline()
    yield


app = FastAPI(title="BioIntel Guardian API", version="1.0.0", lifespan=lifespan)

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IngestPayload(BaseModel):
    source_url: str = ""
    title: str = ""
    abstract: str = ""
    status: str = ""
    timestamp: Optional[str] = None


def _process_drift(event_id: str, payload: dict):
    """Background task: run drift analysis and update the DB row."""
    # Try the service first (set in lifespan for production use),
    # fall back to the global engine (used by tests via dependency_overrides).
    try:
        service = app.state.drift_service
        result = service.process(event_id, payload)
    except AttributeError:
        result = {
            "structural_score": _drift_engine.analyze_payload(payload)["structural_score"],
            "semantic_score": _drift_engine.analyze_payload(payload)["semantic_score"],
            "is_anomalous": _drift_engine.analyze_payload(payload)["is_anomalous"],
        }
    logger.info(
        "Drift analysis complete for %s: structural=%.4f semantic=%.4f anomalous=%s",
        event_id, result["structural_score"], result["semantic_score"], result["is_anomalous"],
    )


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat(), "service": "biointel-guardian"}


@app.post("/api/v1/ingest")
async def ingest(request: Request, background_tasks: BackgroundTasks):
    """Ingest a scrape payload from Bright Data (or mock_webhook_sender).
    Returns 200 immediately; drift analysis runs in the background."""
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    event_id = str(uuid.uuid4())
    ts_raw = payload.get("timestamp")
    ts = None
    if ts_raw:
        try:
            ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            pass

    db = SessionLocal()
    try:
        event = ScrapeEvent(
            id=event_id,
            source_url=payload.get("source_url", ""),
            title=payload.get("title", ""),
            abstract=payload.get("abstract", ""),
            status=payload.get("status", ""),
            timestamp=ts,
            received_at=datetime.now(timezone.utc),
            raw_payload=payload,
        )
        db.add(event)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Failed to persist event: %s", e)
        raise HTTPException(status_code=500, detail="Database write failed")
    finally:
        db.close()

    background_tasks.add_task(_process_drift, str(event_id), payload)

    return {"status": "received", "event_id": str(event_id)}


@app.get("/api/v1/scraper-health")
def scraper_health():
    """Return drift telemetry for the frontend health dashboard."""
    db = SessionLocal()
    try:
        latest = db.query(ScrapeEvent).order_by(ScrapeEvent.received_at.desc()).first()
        if latest is None:
            return {
                "last_run": None,
                "status": "idle",
                "structural_drift_score": 0.0,
                "semantic_drift_score": 0.0,
                "quarantined_items": 0,
                "recent_runs": [],
            }

        quarantined = (
            db.query(ScrapeEvent)
            .filter(ScrapeEvent.is_anomalous == True)
            .count()
        )

        recent = (
            db.query(ScrapeEvent)
            .order_by(ScrapeEvent.received_at.desc())
            .limit(20)
            .all()
        )

        return {
            "last_run": latest.received_at.isoformat() if latest.received_at else None,
            "status": "anomalous" if latest.is_anomalous else "healthy",
            "structural_drift_score": latest.structural_score or 0.0,
            "semantic_drift_score": latest.semantic_score or 0.0,
            "quarantined_items": quarantined,
            "recent_runs": [
                {
                    "id": str(r.id),
                    "source_url": r.source_url,
                    "title": r.title,
                    "status": r.status,
                    "received_at": r.received_at.isoformat() if r.received_at else None,
                    "structural_score": r.structural_score,
                    "semantic_score": r.semantic_score,
                    "is_anomalous": r.is_anomalous,
                }
                for r in recent
            ],
        }
    finally:
        db.close()


@app.get("/api/v1/updates")
def updates(limit: int = 50):
    """Return validated (non-anomalous) research updates for the researcher dashboard."""
    db = SessionLocal()
    try:
        events = (
            db.query(ScrapeEvent)
            .filter(ScrapeEvent.is_anomalous == False)
            .filter(ScrapeEvent.structural_score.isnot(None))
            .order_by(ScrapeEvent.received_at.desc())
            .limit(limit)
            .all()
        )
        return {
            "count": len(events),
            "updates": [
                {
                    "id": str(e.id),
                    "source_url": e.source_url,
                    "title": e.title,
                    "abstract": e.abstract,
                    "status": e.status,
                    "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                    "received_at": e.received_at.isoformat() if e.received_at else None,
                    "structural_score": e.structural_score,
                    "semantic_score": e.semantic_score,
                    "confidence": (
                        "high" if (e.structural_score or 0) < 0.1 and (e.semantic_score or 0) < 0.15
                        else "medium"
                    ),
                }
                for e in events
            ],
        }
    finally:
        db.close()


@app.get("/api/v1/all-events")
def all_events(limit: int = 50):
    """Return all events including anomalous ones for the admin/health view."""
    db = SessionLocal()
    try:
        events = (
            db.query(ScrapeEvent)
            .order_by(ScrapeEvent.received_at.desc())
            .limit(limit)
            .all()
        )
        return {
            "count": len(events),
            "events": [
                {
                    "id": str(e.id),
                    "source_url": e.source_url,
                    "title": e.title,
                    "abstract": e.abstract,
                    "status": e.status,
                    "received_at": e.received_at.isoformat() if e.received_at else None,
                    "structural_score": e.structural_score,
                    "semantic_score": e.semantic_score,
                    "is_anomalous": e.is_anomalous,
                }
                for e in events
            ],
        }
    finally:
        db.close()
