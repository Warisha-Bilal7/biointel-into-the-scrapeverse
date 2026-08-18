Role: Frontend, UI/UX, and Biology/Research Domain Expert
Goal: Define the medical data requirements and build a dual-view Next.js dashboard visualizing both the research and the scraper's health.

0. Domain Definition (Hour 1)

Action: Decide exactly what data matters to a biomedical researcher (e.g., Trial Title, Phase, Status, Abstract, Update Date).

Handoff: Give this exact schema requirement to Tanzeel (so he knows what to scrape) and Warisha (so she knows what keys to validate).

1. Setup & Mocking (Hour 2–4)

Action: Spin up the Next.js/Tailwind app.

Crucial Step: Do not wait for Warisha's API to be deployed. Hardcode a mock JSON response (based on the TDD-sheet.md contract) so you can build the UI immediately.

2. View 1: The Researcher Feed (Hour 5–7)

Action: Build a clean, professional feed of medical updates.

The UX Flex: Add a "Data Confidence" badge next to each article. Green = validated by AI, Yellow/Red = anomaly detected. This visually ties the backend AI to the frontend UX for the judges.

3. View 2: Scraper Health Monitor (Hour 8–10)

Action: Build the "Dev/Admin" dashboard using recharts.

Visuals: Create a line graph tracking the "Semantic Drift Score" over time. Add a visual alert state for when a payload is quarantined (e.g., "Warning: DOM Drift Detected. Payload halted.").

4. Integration (Hour 11+)

Action: Swap your hardcoded mock data with Axios/Fetch calls to the deployed API.
