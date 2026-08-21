"""Bug reproduction test: sample_03_anomalous.json should be flagged as anomalous.

This script goes RED with the current code (bug present) and GREEN after the fix.
"""

import json
import os
import sys

# Force SQLite before any app imports
os.environ["DATABASE_URL"] = "sqlite:///test.db"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.drift import calculate_structural_drift, analyze_payload, STRUCTURAL_THRESHOLD

# Load the anomalous sample payload
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(project_root, "payloads", "sample_03_anomalous.json")) as f:
    payload = json.load(f)

# Test 1: structural drift should exceed threshold → is_anomalous should be True
structural = calculate_structural_drift(payload)
if not (structural > STRUCTURAL_THRESHOLD):
    print(f"BUG CONFIRMED: structural drift={structural}, threshold={STRUCTURAL_THRESHOLD}")
    print("  0.2 > 0.20 is FALSE, so is_anomalous is NOT set even though payload is named 'anomalous'")
    print("  EXPECTED: structural drift should exceed threshold so is_anomalous=True")
    sys.exit(1)  # Bug present - test goes "red"

# Test 2: analyze_payload should flag as anomalous
result = analyze_payload(payload)
if result["is_anomalous"] is not True:
    print(f"BUG CONFIRMED: analyze_payload is_anomalous={result['is_anomalous']}")
    print("  EXPECTED: is_anomalous should be True")
    sys.exit(1)  # Bug present - test goes "red"

print("BUG IS FIXED: all assertions pass - test goes 'green'")