"""
Drift Engine Adapter
====================

Encapsulates the hidden dependencies of the drift detection engine so that
the API endpoint and tests can interact with it through a clear interface
rather than depending on global state.

Principles applied:
  - "The interface is the test surface": every dependency is an explicit
    function/mock parameter, not a hidden global.
  - One adapter = hypothetical seam, two = real: this file defines the seam.
    A second concrete implementation would make it a real seam.
"""

from typing import Optional, Callable, Protocol

from .drift import (
    calculate_structural_drift,
    calculate_semantic_drift,
    _encode,
    _keyword_encode,
    get_baseline_vector,
    STRUCTURAL_THRESHOLD,
    SEMANTIC_THRESHOLD,
)


class TextEncoderProtocol(Protocol):
    """Protocol for text encoding, enabling dependency injection."""

    def encode(self, text: str) -> list[float]: ...


class DriftEngine:
    """Adapter between the API / tests and the drift detection engine.

    Encapsulates the two hidden dependencies that make drift analysis hard
    to test without loading the sentence-transformers model or touching the
    database:

      1. The global model lazy-load in ``_encode()`` / ``_get_model()``.
      2. The DB-dependent baseline vector in ``get_baseline_vector()``.

    Parameters
    ----------
    encoder : TextEncoderProtocol, optional
        Text encoder to use.  Defaults to ``drift.py:_encode`` (which lazy-loads
        the sentence-transformers model and falls back to keyword matching).
    baseline_vector : list[float], optional
        Pre-computed baseline embedding vector.  When provided, ``get_baseline()``
        returns this vector without querying the database.
    get_baseline : Callable[[], Optional[list[float]]], optional
        Function that returns the baseline vector.  Used when ``baseline_vector``
        is not supplied.  Defaults to ``drift.py:get_baseline_vector`` (DB query).
    """

    def __init__(
        self,
        encoder: Optional[TextEncoderProtocol] = None,
        baseline_vector: Optional[list[float]] = None,
        get_baseline: Optional[Callable[[], Optional[list[float]]]] = None,
    ):
        self._encoder = encoder
        self._baseline_vector = baseline_vector
        self._get_baseline = get_baseline

    # ------------------------------------------------------------------
    # Encoder accessor
    # ------------------------------------------------------------------

    def encode(self, text: str) -> list[float]:
        """Encode *text* using the injected encoder or the default ``_encode``."""
        if self._encoder is not None:
            # The injected encoder must conform to TextEncoderProtocol
            return self._encoder(text)
        return _encode(text)

    # ------------------------------------------------------------------
    # Baseline accessor
    # ------------------------------------------------------------------

    def get_baseline(self) -> Optional[list[float]]:
        """Return the baseline vector: injected value > getter function > default."""
        if self._baseline_vector is not None:
            return self._baseline_vector
        if self._get_baseline is not None:
            return self._get_baseline()
        return get_baseline_vector()

    # ------------------------------------------------------------------
    # Public API used by the ingestion pipeline
    # ------------------------------------------------------------------

    def analyze_payload(self, payload: dict) -> dict:
        """Run both drift checks and return an analysis dict.

        This is the same contract as ``drift.analyze_payload`` but with
        dependencies that can be injected for testing.
        """
        structural = calculate_structural_drift(payload)
        abstract = payload.get("abstract", "")
        baseline = self.get_baseline()
        semantic = calculate_semantic_drift(abstract, baseline)

        is_anomalous = structural > STRUCTURAL_THRESHOLD or semantic > SEMANTIC_THRESHOLD

        return {
            "structural_score": round(structural, 4),
            "semantic_score": round(semantic, 4),
            "is_anomalous": is_anomalous,
        }