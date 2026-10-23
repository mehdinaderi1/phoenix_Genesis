"""
Probe XT private API — read-only balance test.
Requires XT_API_KEY and XT_API_SECRET env vars.

Probes: /v4/account/balances, /v4/balances, /v4/asset/balance
"""
import os
import sys
import hmac
import hashlib
import time
import json
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "https://sapi.xt.com"
API_KEY = os.getenv("XT_API_KEY")
API_SECRET = os.getenv("XT_API_SECRET")

if not API_KEY or not API_SECRET:
    print("Set XT_API_KEY and XT_API_SECRET first.")
    print("  $env:XT_API_KEY = 'your-key'")
    print("  $env:XT_API_SECRET = 'your-secret'")
    sys.exit(1)

print(f"API_KEY prefix: {API_KEY[:8]}...")
print(f"API_SECRET prefix: {API_SECRET[:8]}...")
print()

CANDIDATE_ENDPOINTS = [
    ("GET", "/v4/account/balances", None),
    ("GET", "/v4/balances", None),
    ("GET", "/v4/asset/balance", {"coin": "usdt"}),
]


def sign_request(method, path, query_dict=None, body_dict=None):
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"

    # Build header string X (sorted alphabetically)
    headers = {
        "validate-algorithms": "HmacSHA256",
        "validate-appkey": API_KEY,
        "validate-recvwindow": recv_window,
        "validate-timestamp": timestamp,
    }
    x = "&".join(f"{k}={v}" for k, v in sorted(headers.items()))

    # Build Y = #method#path#query#body
    parts = [method, path]
    if query_dict:
        qs = "&".join(f"{k}={v}" for k, v in sorted(query_dict.items()))
        parts.append(qs)
    if body_dict:
        body = json.dumps(body_dict, separators=(",", ":"))
        parts.append(body)
    y = "#" + "#".join(parts)

    original = x + y
    signature = hmac.new(
        API_SECRET.encode("utf-8"),
        original.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return {
        "validate-algorithms": "HmacSHA256",
        "validate-appkey": API_KEY,
        "validate-recvwindow": recv_window,
        "validate-timestamp": timestamp,
        "validate-signature": signature,
    }, (json.dumps(body_dict) if body_dict else None)


def try_endpoint(method, path, query):
    headers, body = sign_request(method, path, query_dict=query)
    url = f"{BASE_URL}{path}"
    if query:
        qs = "&".join(f"{k}={v}" for k, v in sorted(query.items()))
        url = f"{url}?{qs}"

    print(f"  {method} {url}")
    req = urllib.request.Request(
        url,
        headers={**headers, "User-Agent": "PhoenixGenesis/1.0"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            code = data.get("rc") or data.get("code") or 0
            print(f"    HTTP 200, rc={code}, keys={list(data.keys())}")
            if code == 0 or code == "0":
                print(f"    >>> SUCCESS: {path}")
                preview = json.dumps(data, indent=2)[:400]
                print(f"    {preview}")
                return True
            else:
                print(f"    rc non-zero, body: {json.dumps(data)[:200]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        print(f"    HTTP {e.code}: {body}")
    except Exception as e:
        print(f"    Error: {e}")
    return False


def main():
    print("Probing private endpoints (read-only)...")
    for method, path, query in CANDIDATE_ENDPOINTS:
        print()
        if try_endpoint(method, path, query):
            print(f"\n>>> WORKING: {method} {path}")
            return
    print("\n>>> None worked. Check:")
    print("   1. API key permissions (need Read at minimum)")
    print("   2. API key active? (XT may require IP whitelist)")
    print("   3. Base URL (sapi.xt.com correct? maybe testnet differs)")


if __name__ == "__main__":
    main()