# Architecture Diagrams

## 1. Component Diagram

```mermaid
flowchart LR
    A[Target Site] --> B[Bright Data<br/>Scraper Studio]
    B -->|Webhook JSON| C[FastAPI Backend]
    C --> D[(Postgres / pgvector<br/>DB)]
    C --> E[AI Drift Engine<br/>structural + semantic]
    E --> D
    D --> F[Next.js UI<br/>Vercel]
    C -->|REST API| F
```

## 2. Sequence Diagram — Single Data Pull Lifecycle

```mermaid
sequenceDiagram
    participant Cron
    participant Scraper as Bright Data Scraper
    participant API as FastAPI Backend
    participant Engine as Drift Engine
    participant DB as Postgres/pgvector
    participant UI as Next.js Dashboard

    Cron->>Scraper: Trigger scheduled scrape
    Scraper->>Scraper: Extract DOM elements
    Scraper->>API: POST /api/v1/ingest (JSON payload)
    API->>DB: INSERT ScrapeEvent
    API-->>Scraper: 200 OK {status: received, event_id}
    API->>Engine: (background task) analyze_payload()
    Engine->>Engine: structural drift + semantic drift
    Engine->>DB: UPDATE structural_score, semantic_score, is_anomalous
    UI->>API: GET /api/v1/scraper-health (polls every 30s)
    API->>DB: Query latest + recent events
    DB-->>API: Return rows
    API-->>UI: JSON response
    UI->>UI: Render dashboard, show AI DRIFT ALERT if anomalous
```

## 3. State Machine — ScrapeEvent Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Ingested
    Ingested --> Analyzing: Background drift task triggered
    Analyzing --> Validated: structural <= 0.20 AND semantic <= threshold
    Analyzing --> Quarantined: structural > 0.20 OR semantic > threshold
    Validated --> [*]
    Quarantined --> [*]
```

> Note: the semantic threshold shown here is intentionally not hardcoded as a number — see the README's [Drift Detection Engine](../README.md#the-drift-detection-engine) section for the current docs/code discrepancy (`0.35` documented vs. `0.55` in `drift.py`).
