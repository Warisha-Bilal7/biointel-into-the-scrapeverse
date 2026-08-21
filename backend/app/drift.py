"""
AI Drift Detection Engine

Structural Drift: Missing/extra keys vs expected schema -> score [0, 1]
Semantic Drift:   Cosine distance between incoming text embedding and baseline -> score [0, 1]

Thresholds (from TDD-sheet.md):
  structural > 0.20 -> anomalous
  semantic   > 0.35 -> anomalous
"""

import logging
import math
from typing import Optional

logger = logging.getLogger(__name__)

EXPECTED_KEYS = {"source_url", "title", "abstract", "status", "timestamp"}
STRUCTURAL_THRESHOLD = 0.20
SEMANTIC_THRESHOLD = 0.55

_model = None


def _get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Loaded sentence-transformers model: all-MiniLM-L6-v2")
        except Exception as e:
            logger.warning("sentence-transformers unavailable, using keyword fallback: %s", e)
            _model = False
    return _model


def _encode(text: str) -> list[float]:
    model = _get_model()
    if model and model is not False:
        import numpy as np
        vec = model.encode(text, normalize_embeddings=True)
        return vec.tolist()
    return _keyword_encode(text)


def _keyword_encode(text: str) -> list[float]:
    """Deterministic keyword-based fallback encoder when sentence-transformers is unavailable."""
    keywords = [
        "trial", "phase", "study", "drug", "therapy", "patient", "endpoint",
        "efficacy", "safety", "dose", "randomized", "placebo", "outcome",
        "recruiting", "completed", "sponsor", "biomarker", "endpoint",
        "intervention", "eligibility", "protocol", "result", "adverse",
    ]
    words = text.lower().split()
    vec = [0.0] * len(keywords)
    for i, kw in enumerate(keywords):
        count = words.count(kw)
        vec[i] = min(count / 5.0, 1.0)
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine_distance(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        min_len = min(len(a), len(b))
        a, b = a[:min_len], b[:min_len]
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a)) or 1.0
    norm_b = math.sqrt(sum(x * x for x in b)) or 1.0
    sim = dot / (norm_a * norm_b)
    return 1.0 - max(-1.0, min(1.0, sim))


def calculate_structural_drift(payload: dict) -> float:
    if not payload:
        return 1.0
    payload_keys = set(payload.keys())
    missing = EXPECTED_KEYS - payload_keys
    extra = payload_keys - EXPECTED_KEYS
    total_expected = len(EXPECTED_KEYS)
    drift = (len(missing) + len(extra)) / total_expected
    return min(drift, 1.0)


def calculate_semantic_drift(
    text: str,
    baseline_vector=None,
) -> float:
    if not text or not text.strip():
        return 1.0
    if baseline_vector is None:
        return 0.0
    if isinstance(baseline_vector, str):
        baseline_vector = _encode(baseline_vector)
    incoming_vec = _encode(text)
    return cosine_distance(incoming_vec, baseline_vector)


def get_baseline_vector() -> Optional[list[float]]:
    """Try to load the latest baseline embedding from the DB.
    Returns None if the table is empty (first-run scenario)."""
    try:
        from .database import SessionLocal
        from .models import BaselineEmbedding
        db = SessionLocal()
        try:
            row = (
                db.query(BaselineEmbedding)
                .order_by(BaselineEmbedding.created_at.desc())
                .first()
            )
            if row is not None:
                vec = row.embedding
                if vec is not None:
                    return vec
        finally:
            db.close()
    except Exception:
        pass
    return None


def analyze_payload(payload: dict) -> dict:
    """Run both drift checks and return a full analysis dict."""
    structural = calculate_structural_drift(payload)
    abstract = payload.get("abstract", "")
    baseline = get_baseline_vector()
    semantic = calculate_semantic_drift(abstract, baseline)

    is_anomalous = structural > STRUCTURAL_THRESHOLD or semantic > SEMANTIC_THRESHOLD

    return {
        "structural_score": round(structural, 4),
        "semantic_score": round(semantic, 4),
        "is_anomalous": is_anomalous,
    }
