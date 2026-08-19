# System Overview Diagram (Complex)

**Low-Level Architecture — Whole Project with Internal Processing Details**

## PlantText Definition (copy this exact text - this is the complex version)

```planttext
scale 1000 width 1400

actor User
actor "Bright Data" as BD
participant "FastAPI Backend (Full)" as FB
participant "PostgreSQL/pgvector (vectors table)" as DB
participant "AI Drift Engine (with embeddings)" as AI
participant "Next.js UI (pages/api)" as UI
participant "mock_webhook_sender" as MW
participant "Redis Cache (rate limiting)" as RC

User -> BD: 1. Trigger scrape schedule
BD -> FB: 2. POST /api/v1/ingest (webhook payload:{source_url, title, abstract, status, timestamp})
FB -> RC: 3. Check rate limit / cache miss
RC -> FB: 3b. Allow / deny
FB -> DB: 4. INSERT INTO scrape_events (source_url, title, abstract, status, timestamp, received_at)
DB -> FB: 4b. Insert confirm + generated vector_id
FB -> AI: 5. compute_structural_drift(event_data)
AI -> FB: 5b. structural_score, missing_keys_detected
FB -> AI: 6. compute_semantic_drift(event_data.abstract, baseline_vectors)
AI -> FB: 6b. semantic_score, embedding_similarity, embedding_id
FB -> DB: 7. UPDATE scrape_events SET structural_score=X, semantic_score=Y, vector_id=Z, received_at=NOW()
DB -> FB: 7b. Update confirm
FB -> DB: 8. SELECT * FROM scrape_events WHERE received_at > NOW() - INTERVAL '1 hour' ORDER BY received_at DESC LIMIT 20
DB -> FB: 8b. Recent events list
FB -> UI: 9. GET /api/v1/scraper-health {last_run, status, structural_drift_score, semantic_drift_score, quarantined_items, recent_runs}
UI -> User: 10. Dashboard: researcher feed + confidence badges + recent runs table
MW -> FB: 11. POST fallback payloads (if scraper blocked)
FB -> MW: 11b. 200 OK for each fallback

style FB fill:#ffe0b2,stroke:#fb8c00,stroke-width:3px
style DB fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
style AI fill:#ffe0b2,stroke:#fb8c00,stroke-width:3px
style UI fill:#e8f5e9,stroke:#388e3c,stroke-width:3px
style MW fill:#eceff1,stroke:#78909c,stroke-width:1px
style RC fill:#fff59d,stroke:#f6e05e,stroke-width:2px

note right of FB: 
  Drift logic: structural = missing_keys/extra_keys ratio (threshold > 0.20)
  Semantic = cosine_dist(abstract_vector, baseline_vector) (threshold > 0.35)
  is_anomalous = structural > 0.20 OR semantic > 0.35
  
note right of MW: 
  Fallback: 3 pre-saved JSON payloads blown to /api/v1/ingest
  if scraper fails before judging

note right of DB: 
  Schema: scrape_events(id, source_url, title, abstract, status, timestamp, 
    structural_score FLOAT, semantic_score FLOAT, vector_id UUID, received_at TIMESTAMP)
```

## Diagram Description - Enhanced

This **complex low-level UML overview** shows the complete system architecture with internal processing details:

### Expanded Participants

| Symbol | Component | Enhanced Role |
|---|---|---|
| 👤 **User** | Human operator / judge | Initiates scrape, reviews dashboard, sets thresholds |
| 🤖 **Bright Data** (actor) | External scraper service | DOM-targeted extraction, webhook delivery, anti-bot evasion |
| ⚡ **FastAPI Backend (Full)** (participant) | Core logic | Full request lifecycle: validation → drift calc → DB update → health endpoint |
| 🗄️ **PostgreSQL/pgvector (vectors table)** (participant) | Data store | Vector storage for baseline embeddings, pgvector similarity search, audit logging |
| 🧠 **AI Drift Engine (with embeddings)** (participant) | ML logic | Embedding generation (sentence-transformers), cosine similarity computation, drift scoring |
| 📊 **Next.js UI (pages/api)** (participant) | Frontend | API routes: /api/v1/ingest poll, /api/v1/scraper-health, dashboard with dual view |
| ⚠️ **mock_webhook_sender** (participant) | Fallback | 3 payloads, blast mode, idempotency key handling |
| 🗄️ **Redis Cache** (participant) | Rate limiting | Request throttling, cache misses for webhook deduplication, score caching |

### Enhanced Data Flow (11 Steps)

1. **User** triggers **Bright Data** scrape schedule (cron or manual)
2. **Bright Data** scrapes target site → extracts DOM elements → assembles JSON payload `{source_url, title, abstract, status, timestamp}`
3. **Bright Data** sends `POST /api/v1/ingest` webhook to **FastAPI**
4. **FastAPI** checks **Redis Cache** for rate limiting / deduplication key
5. **Redis** returns allow/deny + TTL info
6. **FastAPI** inserts record into **PostgreSQL/pgvector** `scrape_events` table
7. Record gets auto-generated `vector_id` (UUID) and `received_at` timestamp
8. **FastAPI** runs **AI Drift Engine**: 
   - `compute_structural_drift()` → ratio of missing/extra expected keys (threshold: > 0.20)
   - `compute_semantic_drift()` → cosine distance between abstract embedding vs baseline vectors (threshold: > 0.35)
9. **AI Drift Engine** returns: `structural_score`, `missing_keys_detected`, `semantic_score`, `embedding_similarity`, `embedding_id`
10. **FastAPI** updates the `scrape_events` row with scores + embedding IDs + `received_at=NOW()`
11. **FastAPI** serves `GET /api/v1/scraper-health` → UI gets `{last_run, status, structural_drift_score, semantic_drift_score, quarantined_items, recent_runs}`
12. **UI** renders: researcher feed with confidence badges + recent runs table + anomaly alerts
13. If scraper blocked during judging → **mock_webhook_sender** blasts 3 pre-saved JSON payloads to `/api/v1/ingest`

### Key Endpoints (with Internal Details)

| Endpoint | Method | Input (Internal) | Output (Internal) |
|---|---|---|---|
| `/api/v1/ingest` | POST | JSON + Redis check + DB INSERT + drift calc + DB UPDATE | `{"status": "ok", "event_id": "uuid", "scores": {structural: X, semantic: Y}}` |
| `/api/v1/scraper-health` | GET | DB query for latest + score aggregation | `{last_run, status, structural_drift_score, semantic_drift_score, quarantined_items, recent_runs: [...]}` |

### Anomaly Logic (Inside AI Drift Engine)

```
structural_drift = len(missing_keys + extra_keys) / len(expected_keys)
if structural_drift > 0.20: flag += "structural"
semantic_drift = 1 - cosine_sim(abstract_embedding, baseline_embedding)
if semantic_drift > 0.35: flag += "semantic"
is_anomalous = len(flag) > 0
quarantined = is_anomalous AND received_at > now() - 24h
```

### Why This Complex Diagram for This Use Case

- **Shows internal processing**: Unlike simple diagrams, this reveals the actual ML computation pipeline (embedding generation → cosine similarity → drift scoring)
- **Shows data persistence**: pgvector schema, vector IDs, timestamp tracking
- **Shows rate limiting**: Redis cache integration for production readiness
- **Shows complete request lifecycle**: From webhook receipt → score computation → DB update → API response → UI render
- **Shows fallback integration**: mock_webhook_sender interaction with rate-checked endpoint
- **Judges can trace any step**: From trigger → storage → ML → scores → dashboard → fallback
- **Production-ready**: Includes rate limiting, deduplication, vector storage - things a real deployment needs
- **Fits on single page**: Despite complexity, PlantText scaling keeps it readable at 1000x1400

## How to Render

1. Select the PlantText Definition text above (the ```planttext``` code block)
2. Copy it (Ctrl+C or Cmd+C) - this is the complex 11-step version
3. Go to https://www.planttext.com/
4. Click inside the "Diagram Definition" text area
5. Paste the definition (Ctrl+V)
6. The diagram renders automatically — this shows the complete system with internal processing at low level
7. Right-click and select "Save image as..." to download the SVG/PNG

## Generated URL

[Click to render Complex System Overview Diagram](https://www.planttext.com/api/product/diagram/svg?txt=scale%201000%20width%201400%0Aactor%20User%0Aactor%20%22Bright%20Data%22%20as%20BD%0Aparticipant%20%22FastAPI%20Backend%20%28Full%29%22%20as%20FB%0Aparticipant%20%22PostgreSQL%2Fpgvector%20%28vectors%20table%29%22%20as%20DB%0Aparticipant%20%22AIDrift%20Engine%20%28with%20embeddings%29%22%20as%20AI%0Aparticipant%20%22Next.js%20UI%20%28pages%2Fapi%29%22%20as%20UI%0Aparticipant%20%22mock_webhook_sender%22%20as%20MW%0Aparticipant%20%22Redis%20Cache%22%20as%20RC%0AUser%20->%20BD%3A%201.%20Trigger%20scrape%20schedule%0ABD%20->%20FB%3A%202.%20POST%20/api/v1/ingest%20%28webhook%20payload%3A%7Bsource_url%2C%20title%2C%20abstract%2C%20status%2C%20timestamp%7D%29%0AFB%20->%20RC%3A%203.%20Check%20rate%20limit%20%2F%20cache%20miss%0ARC%20->%20FB%3A%203b.%20Allow%20%2F%20deny%0AFB%20->%20DB%3A%204.%20INSERT%20INTO%20scrape_events%20%28source_url%2C%20title%2C%20abstract%2C%20status%2C%20timestamp%2C%20received_at%29%0ADB%20->%20FB%3A%204b.%20Insert%20confirm%20%2B%20generated%20vector_id%0AFB%20->%20AI%3A%205.%20compute_structural_drift%28event_data%29%0AI%20->%20FB%3A%205b.%20structural_score%2C%20missing_keys_detected%0AFB%20->%20AI%3A%206.%20compute_semantic_drift%28event_data.abstract%2C%20baseline_vectors%29%0AI%20->%20FB%3A%206b.%20semantic_score%2C%20embedding_similarity%2C%20embedding_id%0AFB%20->%20DB%3A%207.%20UPDATE%20scrape_events%20SET%20structural_score%3DX%2C%20semantic_score%3DY%2C%20vector_id%3DZ%2C%20received_at%3DNOW%28%29%0ADB%20->%20FB%3A%207b.%20Update%20confirm%0AFB%20->%20DB%3A%208.%20SELECT%20*%20FROM%20scrape_events%20WHERE%20received_at%20%3E%20NOW%28%29%20-%20INTERVAL%20%271%20hour%27%20ORDER%20BY%20received_at%20DESC%20LIMIT%2020%0ADB%20->%20FB%3A%208b.%20Recent%20events%20list%0AFB%20->%20UI%3A%209.%20GET%20/api/v1/scraper-health%20%7Blast_run%2C%20status%2C%20structural_drift_score%2C%20semantic_drift_score%2C%20quarantined_items%2C%20recent_runs%7D%0AUI%20->%20User%3A%2010.%20Dashboard%3A%20researcher%20feed%20%2B%20confidence%20badges%20%2B%20recent%20runs%20table%0AMW%20->%20FB%3A%2011.%20POST%20fallback%20payloads%20%28if%20scraper%20blocked%29%0AFB%20->%20MW%3A%2011b.%20200%20OK%20for%20each%20fallback%0Astyle%20FB%3A%20fill%3A%27ffe0b2%27%2Cstroke%3A%27fb8c00%27%2Cstroke-width%3A3px%0Astyle%20DB%3A%20fill%3A%27e3f2fd%27%2Cstroke%3A%271976d2%27%2Cstroke-width%3A3px%0Astyle%20AI%3A%20fill%3A%27ffe0b2%27%2Cstroke%3A%27fb8c00%27%2Cstroke-width%3A3px%0Astyle%20UI%3A%20fill%3A%27e8f5e9%27%2Cstroke%3A%27388e3c%27%2Cstroke-width%3A3px%0Astyle%20MW%3A%20fill%3A%27eceff1%27%2Cstroke%3A%2778909c%27%2Cstroke-width%3A1px%0Astyle%20RC%3A%20fill%3A%27fff59d%27%2Cstroke%3A%27f6e05e%27%2Cstroke-width%3A2px%0Anote%20right%20of%20FB%3A%0A%20%20Drift%20logic%3A%20structural%20%3D%20missing_keys%2Febs%2Fextra_keys%20ratio%20%28threshold%20%3E%200.20%29%0A%20%20semantic%20%3D%201%20%2D%20cosine_sim%28abstract_embedding%2C%20baseline_embedding%29%20%28threshold%20%3E%200.35%29%0A%20%20is_anomalous%20%3D%20structural%20%3E%200.20%20OR%20semantic%20%3E%200.35%0A%20%20quarantined%20%3D%20is_anomalous%20AND%20received_at%20%3E%20now%28%29%20-%2024h%0Anote%20right%20of%20MW%3A%0A%20%20Fallback%3A%203%20pre-saved%20JSON%20payloads%20blown%20to%20/api/v1/ingest%20%20if%20scraper%20fails%20before%20judging%0Anote%20right%20of%20DB%3A%0A%20%20Schema%3A%20scrape_events%28id%2C%20source_url%2C%20title%2C%20abstract%2C%20status%2C%20timestamp%2C%20structural_score%20FLOAT%2C%20semantic_score%20FLOAT%2C%20vector_id%20UUID%2C%20received_at%20TIMESTAMP%29%0Astyle%20FB%3A%20fill%3A%27ffe0b2%27%2Cstroke%3A%27fb8c00%27%2Cstroke-width%3A3px%0Astyle%20DB%3A%20fill%3A%27e3f2fd%27%2Cstroke%3A%271976d2%27%2Cstroke-width%3A3px%0Astyle%20AI%3A%20fill%3A%27ffe0b2%27%2Cstroke%3A%27fb8c00%27%2Cstroke-width%3A3px%0Astyle%20UI%3A%20fill%3A%27e8f5e9%27%2Cstroke%3A%27388e3c%27%2Cstroke-width%3A3px%0Astyle%20MW%3A%20fill%3A%27eceff1%27%2Cstroke%3A%2778909c%27%2Cstroke-width%3A1px%0Astyle%20RC%3A%20fill%3A%27fff59d%27%2Cstroke%3A%27f6e05e%27%2Cstroke-width%3A2px)

## Related Diagrams

Also available in the `diagrams/` directory:

| Diagram | Focus |
|---|---|
| `component_diagram.md` | Static architecture boundaries (3-view handshake) |
| `sequence_diagram.md` | Runtime lifecycle of a single scrape (8 steps) |
| `state_machine_diagram.md` | Anomaly states (Validated / Quarantined) |
| `system_overview.md` | Low-level complete system interaction (11-step complex version) |
| **`system_overview.md` (complex)** | **Full pipeline with Redis, pgvector schema, embedding internals, anomaly logic** |