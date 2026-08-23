import os
import time
import requests
import argparse
from datetime import datetime, timezone

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
# Your local FastAPI backend URL
BACKEND_INGEST_URL = os.getenv("BACKEND_INGEST_URL", "http://localhost:8000/api/v1/ingest")

def fetch_and_ingest(api_url: str, bearer_token: str):
    """
    Fetches the dataset from Bright Data's API download link and POSTs 
    each record to the local FastAPI backend.
    """
    print(f"[*] Fetching data from Bright Data API...")
    
    headers = {}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        dataset = response.json()
    except Exception as e:
        print(f"[!] Failed to fetch from Bright Data: {e}")
        return

    if not isinstance(dataset, list):
        # Sometimes Bright Data wraps it, handle if it's a single dict or nested
        dataset = [dataset] if not isinstance(dataset, dict) else dataset.get("dataset", [dataset])

    print(f"[*] Successfully downloaded {len(dataset)} records. Sending to backend...")

    success_count = 0
    for record in dataset:
        # Map the payload to match the TDD-sheet.md contract exactly
        # The teammate mentioned they are producing 'pmid' instead of 'status'
        payload = {
            "source_url": record.get("source_url", ""),
            "title": record.get("title", ""),
            "abstract": record.get("abstract", ""),
            # Map PMID to status to avoid structural drift failures, or keep status generic
            "status": record.get("status", f"PMID: {record.get('pmid', 'Unknown')}"),
            "timestamp": record.get("timestamp", datetime.now(timezone.utc).isoformat())
        }

        try:
            res = requests.post(BACKEND_INGEST_URL, json=payload)
            res.raise_for_status()
            success_count += 1
            print(f"  [+] Ingested: {payload['title'][:30]}... -> {res.json().get('event_id')}")
        except Exception as e:
            print(f"  [-] Failed to ingest record: {e}")

    print(f"[*] Done! Successfully ingested {success_count}/{len(dataset)} records.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Bright Data API download and ingest to local backend.")
    parser.add_argument("--url", required=True, help="The Bright Data API Download URL")
    parser.add_argument("--token", required=False, default="", help="Bright Data API Bearer Token (if required)")
    
    args = parser.parse_args()
    fetch_and_ingest(args.url, args.token)
