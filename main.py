import os
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ScrapeVision API")

# --- CORS -------------------------------------------------------------
# CORS_ORIGINS is a comma-separated list, e.g.
# "http://localhost:3000,https://your-frontend.vercel.app"
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for now — swap for Postgres/pgvector writes once the
# ORM models + Drift Math logic land.
_received_events = []


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.post("/webhook/scrape")
async def receive_scrape(request: Request):
    """
    Ingestion endpoint for Bright Data (or mock_webhook_sender.py fallback).
    Expects the JSON shape produced by the Bright Data Scraper Studio
    webhook delivery action.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    event = {
        "received_at": datetime.utcnow().isoformat(),
        "payload": payload,
    }
    _received_events.append(event)

    # TODO: persist to Postgres/pgvector, run Drift Math, update ScrapeEvent
    # state machine (Ingested -> Analyzing -> Validated/Quarantined).

    return {"status": "received", "count": len(_received_events)}


@app.get("/events/recent")
def recent_events(limit: int = 10):
    return _received_events[-limit:]
