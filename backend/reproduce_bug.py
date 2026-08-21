"""Minimal reproducer for structural drift boundary bug.

sample_03_anomalous.json has 4-of-5 keys present, with title="" and status=""
and timestamp missing. Structural drift = 1/5 = 0.2 (exactly at threshold).
Since the anomaly check uses `> 0.20`, it's NOT flagged as anomalous,
even though the payload is named and intended to be anomalous.
"""

import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.drift import calculate_structural_drift, analyze_payload, STRUCTURAL_THRESHOLD

# Load the anomalous sample payload
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(project_root, 'payloads', 'sample_03_anomalous.json')) as f:
    payload = json.load(f)

print("Payload:", json.dumps(payload, indent=2))
print()

structural = calculate_structural_drift(payload)
result = analyze_payload(payload)

print(f"STRUCTURAL_DRIFT: {structural} (threshold: {STRUCTURAL_THRESHOLD})")
print(f"  structural_score: {result['structural_score']}")
print(f"  is_anomalous: {result['is_anomalous']}")
print(f"  Expected: is_anomalous should be True (payload is named 'anomalous')")
print(f"  Bug: structural drift is exactly 0.2, and 0.2 > 0.20 is FALSE")
print()

# Also check: what if we treat empty string values as missing?
expected_keys = {"source_url", "title", "abstract", "status", "timestamp"}
present_keys = set(payload.keys())
missing_via_absence = expected_keys - present_keys

# Check for empty values in present keys
missing_via_empty = set()
for key in present_keys:
    if key in expected_keys and payload[key] == "":
        missing_via_empty.add(key)

all_missing = missing_via_absence | missing_via_empty
drift_via_empty = (len(all_missing) + 0) / len(expected_keys)  # no extra keys
print(f"Keys present: {present_keys}")
print(f"Keys missing via absence: {missing_via_absence}")
print(f"Keys missing via empty value: {missing_via_empty}")
print(f"Total missing keys (with empty-as-missing): {len(all_missing)}")
print(f"Drift with empty-as-missing: {drift_via_empty} (threshold: {STRUCTURAL_THRESHOLD})")
print(f"  Would be anomalous: {drift_via_empty > STRUCTURAL_THRESHOLD}")