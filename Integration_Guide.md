The 3-Way Handshake Protocol

1.Local Tunnels (Warisha & Tanzeel):
Warisha runs the backend locally and exposes it via ngrok. Tanzeel points the Bright Data webhook to the ngrok URL to ensure the scraper can successfully hit the local database.

2.UI Wire-up (Warisha & Arsh):
Arsh points their local Next.js environment (localhost:3000) to Warisha's local FastAPI environment (localhost:8000). Warisha configures CORS to allow localhost:3000.

3.The Cloud Merge (Tanzeel):
Tanzeel deploys both repositories. He updates Bright Data to hit the production backend webhook, and updates the frontend environment variables to point to the production backend API.

4.E2E Validation (Full Team):The team triggers a scrape, verifies the data passes the drift check, and confirms it renders correctly on the live URL.
