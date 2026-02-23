#!/usr/bin/env python3
"""
Smoke test for deployed AgentForge API.
Usage:
  python scripts/smoke_test.py https://your-app.up.railway.app
  python scripts/smoke_test.py
    (uses BASE_URL env var, or http://localhost:8000)
Exits 0 if all checks pass, 1 otherwise.
"""
import json
import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    base = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BASE_URL", "http://localhost:8000")).rstrip("/")

    print(f"Smoke testing: {base}")
    failed = 0

    # 1. GET /health
    try:
        req = urllib.request.Request(f"{base}/health", method="GET")
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            if data.get("status") == "ok":
                print("  GET /health  OK")
            else:
                print("  GET /health  FAIL (status != ok)", data)
                failed += 1
    except Exception as e:
        print("  GET /health  FAIL", e)
        failed += 1

    # 2. POST /chat (requires OPENAI_API_KEY or ANTHROPIC_API_KEY on the server)
    try:
        body = json.dumps({"message": "Do aspirin and ibuprofen interact?"}).encode()
        req = urllib.request.Request(
            f"{base}/chat",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode())
            out = (data.get("output") or "").strip()
            err = data.get("error")
            if out and not err:
                print("  POST /chat   OK (got reply)")
            else:
                print("  POST /chat   FAIL (no output or error)", err or "(empty output)")
                if err:
                    print("    error:", err[:200])
                failed += 1
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print("  POST /chat   FAIL", e.code, body[:200] if body else "")
        failed += 1
    except Exception as e:
        print("  POST /chat   FAIL", e)
        failed += 1

    if failed:
        print("Smoke test FAILED")
        return 1
    print("Smoke test PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
