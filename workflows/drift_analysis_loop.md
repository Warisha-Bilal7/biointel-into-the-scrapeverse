# Workflow: Drift Analysis Loop

## Trigger
- **Event**: New scrape payload arrives via `POST /api/v1/ingest` (from Bright Data webhook or `mock_webhook_sender.py`).
- **Schedule**: Not scheduled; always event-triggered by incoming data.

## Checkpoint
- **Human-in-the-loop at the brief stage**. After the backend processes the payload and drift analysis completes, a brief is presented with the drift scores and anomaly flag.
- **Push right**: Defer the checkpoint as far as possible. The backend does all work (DB write, drift computation, anomaly flagging) before the human is involved. The human is only asked to review the `GET /api/v1/scraper-health` response.

## Brief (human review format)
When `GET /api/v1/scraper-health` is queried, the brief presented to the human includes:
- **`status`**: "anomalous" or "healthy" (based on latest `is_anomalous`)
- **`structural_drift_score`** and **`semantic_drift_score`** for the latest event
- **`quarantined_items`** count — how many events are flagged anomalous
- **Link/reference** to the specific `ScrapeEvent` ID and its `source_url`
- **One-sentence interpretation**: e.g. "Latest payload has structural drift 0.0 and semantic drift 0.0 — within thresholds, marked healthy"

The human's decision: inspect quarantined items, verify confidence levels, or ignore if healthy. Review is fast because all computation is done; only the summary is presented.

## Success metrics
- End-to-end latency from payload ingest to health dashboard update: < 5 seconds
- Brief is always <= 30 words and self-contained (no raw DB output)
- Anomalous events correctly trigger the `is_anomalous` flag per TDD-sheet.md thresholds (structural > 0.20, semantic > 0.35)

## Definition of done
An implementer agent could build this workflow without asking a single question. The spec lists: trigger event (POST /api/v1/ingest), autonomous drift computation, brief format on health check, and the exact API response shape. If any of these are ambiguous, the spec is not done.