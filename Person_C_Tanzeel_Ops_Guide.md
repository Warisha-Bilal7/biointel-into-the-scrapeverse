Role: Architecture, Integration, Testing, Bright Data, and Deployment
Goal: Connect Warisha's backend to Arsh's frontend, configure the scraper, manage E2E testing, and build the final pitch assets.

1. Bright Data Extraction (Hour 1–4) ✅ COMPLETED
Action: Used Bright Data Scraper Studio on the target site Arsh selected.
Targeting: Configured DOM targeting per Arsh's domain definition.
Delivery: Configured Webhook delivery to push JSON to Warisha's FastAPI backend (http://localhost:8000/api/v1/ingest) via ngrok tunnel.
Verification: Confirmed payload structure matches backend expectations - JSON includes source_url, title, abstract, status, timestamp.

2. Cloud Deployment & Dockerization (Hour 5–8) ✅ COMPLETED
Action: Containerized Warisha's FastAPI and PostgreSQL/pgvector environment using Docker Compose.
Deployment: Deployed backend to cloud provider (Render/Railway/AWS). Deployed Arsh's Next.js frontend to Vercel.
Configuration: Updated Bright Data webhook to point to live backend URL. Ensured backend CORS accepts Vercel frontend URL.

3. E2E Testing & Fallback Generation (Hour 9–10) ✅ COMPLETED
Action: Ran end-to-end testing. Triggered manual scrape and confirmed it appeared on live Vercel site.
The Safety Net: Wrote mock_webhook_sender.py script. If target website blocks scraper right before judging, use this script to blast pre-saved JSON payloads to backend so live demo still works flawlessly.
Fallback payloads: Pre-saved sample JSON payloads ready to blast if scraper gets blocked during judging.

4. Architecture Diagrams & Pitch Prep (Hour 11+) ✅ COMPLETED
Action: Created UML files to include in Devpost submission and README.
Required Diagrams (use Draw.io or Mermaid - all embedded in README):
- Component Diagram: Target Site → Bright Data → FastAPI → Postgres/pgvector (DB) & AI Engine → Next.js UI.
- Sequence Diagram: Lifecycle of single data pull (Cron → Scrape → Drift Math → DB → Dashboard).
- State Machine: States of ScrapeEvent (e.g., Ingested → Analyzing → Validated / Quarantined).

Exit criteria: All 3 diagrams complete and embedded in README/Devpost.

Summary Timeline
```
Hr 1–4   | Bright Data scraper + webhook (test endpoint) ✅
Hr 5–8   | Dockerize + deploy backend & frontend, CORS, webhook → prod ✅
Hr 9–10  | E2E test + mock_webhook_sender.py fallback ✅
Hr 11+   | Diagrams (component, sequence, state machine) + submission ✅
```

Dependencies on Others
- **Arsh**: domain definition (DOM targets) needed before Phase 1 ✅ (provided)
- **Warisha**: FastAPI/Postgres backend code needed before Phase 2 ✅ (delivered)
- **Tanzeel**: Bright Data webhook configured, backend deployed, CORS tested ✅

Risks & Mitigations
- **Risk**: Target site blocks scraper during judging → **Mitigation**: mock_webhook_sender.py fallback (Phase 3.2) ✅ tested
- **Risk**: CORS misconfiguration breaks frontend-backend link → **Mitigation**: Test CORS explicitly in Phase 2.5 before E2E testing ✅ verified
- **Risk**: Webhook URL not updated after deployment → **Mitigation**: Checklist step 2.4, verified before Phase 3 ✅