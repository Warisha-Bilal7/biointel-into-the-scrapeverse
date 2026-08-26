import uuid
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import ScrapeEvent
from ..drift_adapter import DriftEngine


class DriftProcessingService:
    """Service that encapsulates background drift processing.

    Responsibilities:
    - Run drift analysis via an injected DriftEngine instance.
    - Persist the analysis results to the ScrapeEvent row in the database.
    - Handle its own DB session lifecycle for use in FastAPI background tasks.

    Principles applied:
    - "The interface is the test surface": every dependency (DriftEngine) is
      an explicit constructor parameter, not a hidden global.
    - One adapter = hypothetical seam, two = real: this file defines the seam.
      A second concrete implementation (e.g., a mock) would make it a real
      seam for testing.
    """

    def __init__(self, engine: DriftEngine) -> None:
        self._engine = engine

    def process(self, event_id: str, payload: Dict[str, Any]) -> Dict[str, float]:
        """Run drift analysis and persist results for the given event.

        Parameters
        ----------
        event_id : str
            The database row ID of the ScrapeEvent to update.
        payload : dict
            The incoming payload dict (5-key expected schema).

        Returns
        -------
        dict
            ``{
                "structural_score": float,
                "semantic_score": float,
                "is_anomalous": bool,
            }``
        """
        db: Session = SessionLocal()
        try:
            event = db.query(ScrapeEvent).filter(ScrapeEvent.id == event_id).first()
            if event is None:
                return {"structural_score": 1.0, "semantic_score": 0.0, "is_anomalous": True}

            analysis = self._engine.analyze_payload(payload)
            event.structural_score = analysis["structural_score"]
            event.semantic_score = analysis["semantic_score"]
            event.is_anomalous = analysis["is_anomalous"]

            if not analysis["is_anomalous"]:
                abstract = payload.get("abstract", "")
                if abstract:
                    vec = self._engine.encode(abstract)
                    event.vector_id = str(uuid.uuid4())

            db.commit()

            return {
                "structural_score": round(event.structural_score, 4),
                "semantic_score": round(event.semantic_score, 4),
                "is_anomalous": event.is_anomalous,
            }
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()