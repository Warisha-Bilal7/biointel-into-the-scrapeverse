# Valid vs Minimal Payloads

Description: Distinguish between valid payloads with all 5 required keys and minimal payloads with only 1 key.

Reference implementation: structural drift calculation with expected keys set.
- Structural drift = 0 for valid 5-key payloads
- Structural drift > 0.20 for minimal 1-key payloads
