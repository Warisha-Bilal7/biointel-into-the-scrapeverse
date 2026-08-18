Role: Backend + AI Drift Detection (FastAPI, pgvector, Embeddings)
Goal: Ingest payloads, detect structural/semantic drift, and serve validated data to the frontend.

0. Setup (15 min)

Bash
cd backend
pip install fastapi uvicorn pytest httpx sentence-transformers psycopg2-binary pgvector --break-system-packages
mkdir -p app
Note: Person C will handle the Dockerization later. Focus purely on local logic first.

1. Database & Baseline Setup (Hour 1–2)

Action: Build the PostgreSQL + pgvector schema. Create tables for ScrapeEvents and ResearchArticles.

Vectorization: Ensure ResearchArticles has a vector column for the baseline embeddings.

Test Goal: Make test_db_connection.py pass locally.

2. The AI Drift Engine (Hour 3–5)

Action: Load a lightweight sentence transformer (e.g., all-MiniLM-L6-v2) to run locally without rate limits.

Structural Drift: Write calculate_structural_drift(payload). Check for missing keys expected by the Biology domain (defined by Person B).

Semantic Drift: Write calculate_semantic_drift(new_text, baseline_vector). Convert text to an embedding and calculate cosine distance.

Test Goal: Make test_drift_logic.py pass. It must successfully flag garbage text (like website footers) masquerading as medical data.

3. Webhook Ingestion API (Hour 6–7)

Action: Build POST /api/v1/ingest for Person C's scraper to hit. It must return a 200 OK immediately and process the drift math asynchronously so the scraper doesn't timeout.

4. Frontend API Endpoints (Hour 8)

Action: Build GET /api/v1/updates (returns clean data for the researcher feed) and GET /api/v1/scraper-health (returns drift telemetry).
