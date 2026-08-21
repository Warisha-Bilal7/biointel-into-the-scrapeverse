import json
import os
import sys

# Force SQLite
os.environ["DATABASE_URL"] = "sqlite:///test.db"
sys.path.insert(0, ".")

from app.drift import calculate_structural_drift, analyze_payload, STRUCTURAL_THRESHOLD

# Load the anomalous sample payload
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(project_root, "payloads", "sample_03_anomalous.json")) as f:
    payload = json.load(f)

structural = calculate_structural_drift(payload)
result = analyze_payload(payload)

print(f"structural_drift: {structural} (threshold: {STRUCTURAL_THRESHOLD})")
print(f"is_anomalous: {result['is_anomalous']}")
print(f"BUG FIXED: {result['is_anomalous'] == True and structural > STRUCTURAL_THRESHOLD}")