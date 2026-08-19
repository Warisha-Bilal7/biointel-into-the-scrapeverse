#!/usr/bin/env python3
"""
mock_webhook_sender.py

Safety-net script for demo day. If the target site blocks the Bright Data
scraper right before judging, run this to replay pre-saved JSON payloads
to the backend so the live dashboard still updates in real time.

Usage:
    python mock_webhook_sender.py --url http://localhost:8000/webhook/scrape
    python mock_webhook_sender.py --url https://your-backend.onrender.com/webhook/scrape --interval 5
    python mock_webhook_sender.py --once payloads/sample_01.json

Payload files:
    Place one or more pre-saved JSON payloads (matching the real Bright
    Data webhook shape) in the `payloads/` directory. By default the
    script cycles through them in order, looping forever, one every
    `--interval` seconds.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import requests

DEFAULT_PAYLOAD_DIR = Path(__file__).parent / "payloads"


def load_payloads(payload_dir: Path) -> list[dict]:
    files = sorted(payload_dir.glob("*.json"))
    if not files:
        print(f"[!] No .json payload files found in {payload_dir}", file=sys.stderr)
        sys.exit(1)

    payloads = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                payloads.append({"file": f.name, "data": json.load(fh)})
        except json.JSONDecodeError as e:
            print(f"[!] Skipping {f.name} — invalid JSON: {e}", file=sys.stderr)
    if not payloads:
        print("[!] No valid payloads to send.", file=sys.stderr)
        sys.exit(1)
    return payloads


def send(url: str, payload: dict, timeout: float = 10.0) -> bool:
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"[!] Send failed: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Replay pre-saved scrape payloads to the backend webhook.")
    parser.add_argument("--url", required=True, help="Backend webhook URL, e.g. http://localhost:8000/webhook/scrape")
    parser.add_argument("--payload-dir", default=str(DEFAULT_PAYLOAD_DIR), help="Directory of .json payload files")
    parser.add_argument("--interval", type=float, default=10.0, help="Seconds between sends when looping (default: 10)")
    parser.add_argument("--once", metavar="FILE", help="Send a single specific payload file and exit")
    parser.add_argument("--loop", action="store_true", help="Cycle through all payloads forever (Ctrl+C to stop)")
    args = parser.parse_args()

    if args.once:
        path = Path(args.once)
        if not path.exists():
            print(f"[!] File not found: {path}", file=sys.stderr)
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        ok = send(args.url, data)
        print(f"[{'OK' if ok else 'FAIL'}] {path.name} -> {args.url}")
        sys.exit(0 if ok else 1)

    payload_dir = Path(args.payload_dir)
    payloads = load_payloads(payload_dir)
    print(f"[i] Loaded {len(payloads)} payload(s) from {payload_dir}")
    print(f"[i] Target: {args.url}")

    if not args.loop:
        # Single pass through all payloads
        for p in payloads:
            ok = send(args.url, p["data"])
            print(f"[{'OK' if ok else 'FAIL'}] {p['file']} -> {args.url}")
            time.sleep(args.interval)
        return

    print(f"[i] Looping every {args.interval}s — Ctrl+C to stop")
    i = 0
    try:
        while True:
            p = payloads[i % len(payloads)]
            ok = send(args.url, p["data"])
            print(f"[{'OK' if ok else 'FAIL'}] {p['file']} -> {args.url}")
            i += 1
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n[i] Stopped.")


if __name__ == "__main__":
    main()
