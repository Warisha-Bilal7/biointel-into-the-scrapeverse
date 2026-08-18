1. The API Contract (The Single Source of Truth)If any person needs to change these keys, all three members must sync immediately.Tanzeel (Scraper) $\rightarrow$ Warisha (Backend): POST /api/v1/ingestJSON{
  "source_url": "https://...",
  "title": "Phase 3 Trial...",
  "abstract": "The study evaluates...",
  "status": "Recruiting",
  "timestamp": "2026-08-18T20:00:00Z"
}
Warisha (Backend) $\rightarrow$ Arsh (Frontend): GET /api/v1/scraper-healthJSON{
  "last_run": "2026-08-18T20:05:00Z",
  "status": "anomalous",
  "structural_drift_score": 0.45,
  "semantic_drift_score": 0.82,
  "quarantined_items": 12
}

2. Drift Math (For Warisha's Pytest Suite)
Semantic Distance ($D_{sem}$): Cosine distance between the incoming text vector and the baseline vector.Test Constraint: If $D_{sem} > 0.35$, the test must assert is_anomalous == True.
Structural Drift ($D_{str}$): Missing keys / Expected keys.Test Constraint: If $D_{str} > 0.20$, the test must assert is_anomalous == True.
