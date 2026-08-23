#!/usr/bin/env python3
"""Run the backend test suite."""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_backend.py", "-v"],
    cwd="C:/Users/FATTANI COMPUTERS/Documents/biointel-into-the-scrapeverse/backend",
    capture_output=True,
    text=True,
)

print("STDOUT:")
print(result.stdout)
print("STDERR:")
print(result.stderr)
print("Return code:", result.returncode)