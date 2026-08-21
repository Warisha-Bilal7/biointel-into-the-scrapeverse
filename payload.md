## Approach: sample_01.json — full 5-key payload
**Status**: ✅ SUCCEEDED (baseline expectation)
**Payload Shape**: {"source_url": "https://clinicaltrials.gov/study/NCT05901234", "title": "Phase 3 Randomized Trial of Pembrolizumab Plus Chemotherapy in Metastatic Non-Small Cell Lung Cancer", "abstract": "This phase 3, double-blind, randomized, placebo-controlled trial evaluates the efficacy and safety of pembrolizumab in combination with platinum-based chemotherapy versus placebo plus chemotherapy in participants with previously untreated metastatic non-small cell lung cancer whose tumors express PD-L1. Primary endpoint is overall survival. Secondary endpoints include progression-free survival and objective response rate. Study is currently recruiting across 120 sites in 28 countries.", "status": "Recruiting", "timestamp": "2026-08-20T08:00:00Z"}
**Key Lesson**: All 5 expected keys present → structural drift = 0.0; abstract matches baseline vector → semantic drift ≈ 0.0; is_anomalous = False
**Avoid**: Omitting any of the 5 keys (source_url, title, abstract, status, timestamp)
**Used In**: test_structural_drift_valid_payload() — pytest test #1; also the standard API ingest payload

## Approach: Minimal payload — only source_url
**Status**: ✅ SUCCEEDED (triggers anomaly)
**Payload Shape**: {"source_url": "https://example.com"}
**Key Lesson**: 4 keys missing out of 5 expected → structural drift = 4/5 = 0.8 > 0.20 threshold → is_anomalous = True
**Avoid**: Payload with 1-2 keys only if you want non-anomalous results; structural drift will always exceed 0.20
**Used In**: test_structural_drift_missing_keys_anomalous() — pytest test #2; also sample_03_anomalous.json

## Approach: Biomedical abstract similar to baseline
**Status**: ✅ SUCCEEDED (within threshold)
**Payload Shape**: {"source_url": "...", "title": "...", "abstract": "A phase 3 double-blind study assessing the safety and efficacy of a new drug in patients with the same chronic condition. The primary endpoint measures disease severity reduction.", "status": "Recruiting", "timestamp": "..."}
**Key Lesson**: Abstract text with high keyword overlap to baseline → cosine similarity high → semantic score ≤ 0.35 → is_anomalous = False
**Avoid**: Abstracts with dramatically different terminology (non-clinical, non-biomedical language) — those cross the 0.35 threshold
**Used In**: test_semantic_drift_similar_text() — pytest test #3

## Approach: Cookie policy / website footer text as abstract
**Status**: ✅ SUCCEEDED (triggers anomaly)
**Payload Shape**: {"source_url": "...", "title": "Footer Content", "abstract": "Click here to accept cookies. Terms of service apply. Copyright 2026 Website Inc. All rights reserved. Follow us on Twitter. Privacy policy.", "status": "Unknown", "timestamp": "..."}
**Key Lesson**: Non-biomedical, repetitive keyword-dense text → low keyword overlap with baseline → cosine distance > 0.35 → semantic score high → is_anomalous = True
**Avoid**: Using this pattern for valid data — it's strictly a drift-triggering test payload, not real trial data
**Used In**: test_semantic_drift_garbage_text_anomalous() — pytest test #4; sample_03_anomalous.json

## Approach: Protocol drift payload — sample_02_protocol_drift.json
**Status**: ✅ SUCCEEDED (mixed drift behavior)
**Payload Shape**: {"source_url": "https://clinicaltrials.gov/study/NCT05901234", "title": "Phase 3 Trial of Pembrolizumab Plus Chemotherapy in Non-Small Cell Lung Cancer", "abstract": "This study evaluates pembrolizumab with chemotherapy in patients with metastatic non-small cell lung cancer expressing PD-L1. Primary endpoint is overall survival. Note: The primary endpoint has been revised from progression-free survival to overall survival as of protocol amendment v3.0 dated 2026-07-15. Secondary endpoints now include patient-reported outcomes. Study status updated to active, not recruiting pending safety review.", "status": "Active, not recruiting", "timestamp": "2026-08-20T10:30:00Z"}
**Key Lesson**: Status field change doesn't directly trigger structural drift (all 5 keys present), but abstract containing amendment notes may increase semantic distance from baseline; structural score = 0.0, semantic score depends on text content
**Avoid**: Assuming status change alone affects drift — only structural keys matter for structural drift; semantic drift depends entirely on abstract text similarity
**Used In**: payloads/ directory — fallback data; manual E2E testing; protocol change scenario

## Approach: python mock_webhook_sender.py --once payloads/sample_01.json
**Status**: ✅ SUCCEEDED (one-shot mode)
**Payload Shape**: Same as sample_01.json — 5-key valid trial payload
**Key Lesson**: `--once` flag sends exactly one file and exits; useful for quick E2E validation without looping; returns 200 + event_id from backend
**Avoid**: Forgetting `--url` argument — script will prompt for it; also ensure backend is running first
**Used In**: Phase 3 E2E testing fallback; demo-day safety net; quick verification payload