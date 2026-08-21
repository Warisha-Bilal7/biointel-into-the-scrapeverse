# Workflow: Test Loop

## Trigger
- **Event**: `pytest` discovery on `backend/tests/test_backend.py`. Runs as part of each development iteration, CI/CD pipeline, or before a demo/day validation.
- **Schedule**: Not scheduled; always event-triggered by a developer running tests locally or in CI.

## Checkpoint
- **None** (autonomous). All test results are collected and displayed; the human is involved only if a test fails.
- **Push right**: The checkpoint is pushed as far as possible — the human is asked only when a test goes red, with the full output, failure location, and minimised repro already prepared.

## Brief (human review format)
When a test failure occurs, the brief presented to the human includes:
- **Which test(s) failed** (test names)
- **Exact error message** (truncated to the core assertion failure)
- **Link/referenc** e to the failing assertion in `test_backend.py`
- **Minimised reproduction** (the smallest payload/scenario that triggers the failure, if applicable)
- **One-sentence summary** of what the test validates

The human's decision: rerun, investigate, skip, or update the test. Speed of review is imperative — the brief is designed to be read in under 30 seconds.

## Success metrics
- Loop runs in < 30 seconds (currently ~37s with pytest collection warnings)
- 100% of test output is actionable (no opaque "import errors" without source context)
- Zero "silent failures" — every red run reveals the exact symptom

## Definition of done
An implementer agent could build this workflow without asking a single question. The spec lists: trigger event, autonomous execution, brief format on failure, and the exact files involved. If any of these are ambiguous, the spec is not done.

---
---
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

---
---
# Workflow: Mock Webhook Sender Loop

## Trigger
- **Event**: Manual invocation by the operator. `python mock_webhook_sender.py <url>` — sends one or all pre-saved payloads to the backend.
- **Schedule**: Not on a schedule; triggered on demand (E2E testing, demo day, scraper-blocked fallback).

## Checkpoint
- **Human-in-the-loop at the result stage**. After the script sends payloads, the human reviews the responses (200 + event_id, or errors).
- **Push right**: Defer the checkpoint as far as possible. The script does all work (reading payloads, sending HTTP POST, collecting responses) before the human is involved. The human is only asked to verify the outcomes.

## Brief (human review format)
After running `python mock_webhook_sender.py http://localhost:8000/api/v1/ingest`, the brief presented to the human includes:
- **`status`** from each payload send: "received" or error detail
- **`event_id`** for successfully ingested payloads
- **List of payloads sent** (file names from `payloads/` directory) and their outcomes
- **Any errors** (HTTP status codes, connection failures)
- **One-sentence summary**: e.g. "3/3 payloads received; sample_02 had status 200 with event_id xxxx"

The human's decision: proceed to frontend review, debug a failed payload, or adjust sample data. Review is fast because the script collects and reports all outcomes.

## Success metrics
- Script exits cleanly after sending specified payloads
- All 3 sample payloads (sample_01, sample_02, sample_03) are sendable without modification
- Response time per payload: < 1 second (backend processing time)
- `--once` flag sends exactly one file and exits as expected

## Definition of done
An implementer agent could build this workflow without asking a single question. The spec lists: trigger command (`python mock_webhook_sender.py <url>`), payload files from `payloads/`, expected response format (`status` + `event_id`), and the `--once` flag behavior. If any of these are ambiguous, the spec is not done.