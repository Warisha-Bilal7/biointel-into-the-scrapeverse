import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.drift import calculate_structural_drift, calculate_semantic_drift, analyze_payload, _encode, get_baseline_vector, STRUCTURAL_THRESHOLD, SEMANTIC_THRESHOLD

# Load sample payloads - from project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(project_root, 'payloads', 'sample_01.json')) as f:
    p1 = json.load(f)
with open(os.path.join(project_root, 'payloads', 'sample_02_protocol_drift.json')) as f:
    p2 = json.load(f)
with open(os.path.join(project_root, 'payloads', 'sample_03_anomalous.json')) as f:
    p3 = json.load(f)

print('=== sample_01.json (full payload) ===')
s = calculate_structural_drift(p1)
a = analyze_payload(p1)
print(f'  structural_drift: {s} (threshold: {STRUCTURAL_THRESHOLD}) -> anomalous: {s > STRUCTURAL_THRESHOLD}')
print(f'  analyze_payload: {a}')

print()
print('=== sample_02_protocol_drift.json ===')
s = calculate_structural_drift(p2)
a = analyze_payload(p2)
print(f'  structural_drift: {s} (threshold: {STRUCTURAL_THRESHOLD}) -> anomalous: {s > STRUCTURAL_THRESHOLD}')
print(f'  analyze_payload: {a}')

print()
print('=== sample_03_anomalous.json ===')
s = calculate_structural_drift(p3)
a = analyze_payload(p3)
print(f'  structural_drift: {s} (threshold: {STRUCTURAL_THRESHOLD}) -> anomalous: {s > STRUCTURAL_THRESHOLD}')
print(f'  analyze_payload: {a}')