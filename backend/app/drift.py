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
from typing import Optional, Callable

logger = logging.getLogger(__name__)

EXPECTED_KEYS_DEFAULT = {"source_url", "title", "abstract", "status", "timestamp"}
STRUCTURAL_THRESHOLD = 0.20
SEMANTIC_THRESHOLD = 0.55


# ---------------------------------------------------------------------------
# Protocol for dependency injection
# ---------------------------------------------------------------------------

class TextEncoderProtocol:
    """Protocol for text encoding, enabling dependency injection.

    Implementers must define an ``encode`` method that takes a string and
    returns a normalised embedding vector (list of floats).
    """

    def encode(self, text: str) -> list[float]: ...


# ---------------------------------------------------------------------------
# Global model state — now fully injectable
# ---------------------------------------------------------------------------

_model: Optional[object] = None  # type: ignore[assignment]  # lazy-loaded SentenceTransformer or False


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


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _encode(
    text: str,
    encoder: Optional[TextEncoderProtocol] = None,
) -> list[float]:
    """Encode *text* using the injected *encoder* or the default lazy-load.

    Parameters
    ----------
    text : str
        Input text to encode.
    encoder : TextEncoderProtocol, optional
        If provided, used instead of the global model lazy-load.
        Defaults to ``None``, which loads the sentence-transformers model
        once and falls back to ``_keyword_encode``.

    Returns
    -------
    list[float]
        Normalised embedding vector.
    """
    if encoder is not None:
        return encoder.encode(text)
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


def cosine_distance(
    a: list[float],
    b: list[float],
) -> float:
    """Cosine distance between two vectors."""
    if len(a) != len(b):
        min_len = min(len(a), len(b))
        a, b = a[:min_len], b[:min_len]
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a)) or 1.0
    norm_b = math.sqrt(sum(x * x for x in b)) or 1.0
    sim = dot / (norm_a * norm_b)
    return 1.0 - max(-1.0, min(1.0, sim))


# ---------------------------------------------------------------------------
# Payload normalization
# ---------------------------------------------------------------------------

def normalize_payload(
    payload: dict,
    expected_keys: Optional[set] = None,
) -> set:
    """Return the set of payload keys that are "missing" (absent or empty/None).

    Parameters
    ----------
    payload : dict
        The incoming payload dict.
    expected_keys : set, optional
        Keys that are expected.  Defaults to ``EXPECTED_KEYS_DEFAULT``
        ``{"source_url", "title", "abstract", "status", "timestamp"}``.

    Returns
    -------
    set
        Keys from ``expected_keys`` that are absent or have empty/None values.
    """
    if not payload:
        return EXPECTED_KEYS_DEFAULT if not expected_keys else expected_keys
    expected = expected_keys or EXPECTED_KEYS_DEFAULT
    payload_keys = set(payload.keys())
    missing = expected - payload_keys
    # Treat keys with empty/None values as missing data
    for key in payload_keys:
        if key in expected and not payload[key]:
            missing.add(key)
    return missing


# ---------------------------------------------------------------------------
# Structural drift
# ---------------------------------------------------------------------------

def calculate_structural_drift(
    payload: dict,
    expected_keys: Optional[set] = None,
) -> float:
    """Structural drift: missing / extra keys vs expected schema.

    This function is now purely about key-set mathematics — it does not
    inspect payload values.  The "missing" set is obtained via
    ``normalize_payload`` so that the interface concentrates on the drift
    score calculation rather than value inspection.

    Parameters
    ----------
    payload : dict
        The incoming payload dict.
    expected_keys : set, optional
        Keys that are expected.  Defaults to ``EXPECTED_KEYS_DEFAULT``
        ``{"source_url", "title", "abstract", "status", "timestamp"}``.

    Returns
    -------
    float
        Drift score in ``[0, 1]``.  ``0`` = no drift, ``1`` = maximally drift.
    """
    if not payload:
        return 1.0
    expected = expected_keys or EXPECTED_KEYS_DEFAULT
    payload_keys = set(payload.keys())
    missing = normalize_payload(payload, expected_keys=expected_keys or set())
    extra = payload_keys - expected
    total_expected = len(expected)
    drift = (len(missing) + len(extra)) / total_expected
    return min(drift, 1.0)


# ---------------------------------------------------------------------------
# Semantic drift
# ---------------------------------------------------------------------------

def calculate_semantic_drift(
    text: str,
    baseline_vector: Optional[list[float]] = None,
    encoder: Optional[TextEncoderProtocol] = None,
) -> float:
    """Semantic drift: cosine distance between incoming text and baseline.

    Parameters
    ----------
    text : str
        Incoming text to compare.
    baseline_vector : list[float], optional
        Pre-computed baseline embedding.  If ``None``, returns ``0.0``.
        If provided as a string, it is encoded via *encoder*.
    encoder : TextEncoderProtocol, optional
        Used to encode *text* and (if *baseline_vector* is a string) the
        baseline.  If ``None``, the default ``_encode`` (with global model
        lazy-load) is used.

    Returns
    -------
    float
        Semantic distance in ``[0, 1]``.  ``0`` = identical, ``1`` = maximally
        different.
    """
    if not text or not text.strip():
        return 1.0
    if baseline_vector is None:
        return 0.0
    if isinstance(baseline_vector, str):
        baseline_vector = _encode(baseline_vector, encoder=encoder)
    incoming_vec = _encode(text, encoder=encoder)
    return cosine_distance(incoming_vec, baseline_vector)


# ---------------------------------------------------------------------------
# Baseline vector
# ---------------------------------------------------------------------------

def get_baseline_vector(
    get_baseline: Optional[Callable[[], Optional[list[float]]]] = None,
) -> Optional[list[float]]:
    """Return the baseline vector.

    Parameters
    ----------
    get_baseline : Callable[[], Optional[list[float]]], optional
        Function that returns the baseline vector.  When provided, called
        instead of querying the database.  Defaults to ``None``, which
        performs the DB query (original behaviour).

    Returns
    -------
    Optional[list[float]]
        The baseline embedding, or ``None`` if unavailable.
    """
    if get_baseline is not None:
        return get_baseline()
    # Original DB-query behaviour (kept for backward compatibility)
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


# ---------------------------------------------------------------------------
# Payload analysis
# ---------------------------------------------------------------------------

def analyze_payload(
    payload: dict,
    encoder: Optional[TextEncoderProtocol] = None,
    get_baseline: Optional[Callable[[], Optional[list[float]]]] = None,
) -> dict:
    """Run both drift checks and return a full analysis dict.

    This is the same contract as the original ``analyze_payload`` but with
    dependencies that can be injected for testing.

    Parameters
    ----------
    payload : dict
        The incoming payload dict (5-key expected schema).
    encoder : TextEncoderProtocol, optional
        Used by ``calculate_semantic_drift`` to encode text.  Defaults to
        ``None``, which uses the global model lazy-load.
    get_baseline : Callable[[], Optional[list[float]]], optional
        Function that returns the baseline embedding.  When ``None``, the
        database is queried (original behaviour).

    Returns
    -------
    dict
        ``{
            "structural_score": float,
            "semantic_score": float,
            "is_anomalous": bool,
        }``
    """
    structural = calculate_structural_drift(payload)
    abstract = payload.get("abstract", "")
    baseline = get_baseline_vector(get_baseline=get_baseline)
    semantic = calculate_semantic_drift(abstract, baseline, encoder=encoder)

    is_anomalous = structural > STRUCTURAL_THRESHOLD or semantic > SEMANTIC_THRESHOLD

    return {
        "structural_score": round(structural, 4),
        "semantic_score": round(semantic, 4),
        "is_anomalous": is_anomalous,
    }