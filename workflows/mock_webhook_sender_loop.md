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