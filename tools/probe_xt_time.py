"""
Probe XT private API — with server time sync.
Fixes AUTH_105 (outdated timestamp).
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
    sys.exit(1)

print(f"API_KEY prefix: {API_KEY[:8]}...")
print()

# ─── 1. Fetch server time ───
print("Fetching server time from XT...")
try:
    req = urllib.request.Request(
        f"{BASE_URL}/v4/public/time",
        headers={"User-Agent": "PhoenixGenesis/1.0"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        server_time = data.get("result", {}).get("serverTime") or data.get("result")
        if isinstance(server_time, str):
            server_time = int(server_time)
        print(f"  server_time: {server_time}")
except Exception as e:
    print(f"  failed to fetch server time: {e}")
    server_time = int(time.time() * 1000)

local_time = int(time.time() * 1000)
offset_ms = server_time - local_time
print(f"  local_time:  {local_time}")
print(f"  offset:      {offset_ms:+d} ms ({offset_ms/1000:+.2f} sec)")
print()


# ─── 2. Signature ───
def sign(method, path, query=None, body=None, recv_window=60000):
    timestamp = str(int(time.time() * 1000) + offset_ms)

    headers = {
        "validate-algorithms": "HmacSHA256",
        "validate-appkey": API_KEY,
        "validate-recvwindow": str(recv_window),
        "validate-timestamp": timestamp,
    }
    x = "&".join(f"{k}={v}" for k, v in sorted(headers.items()))

    parts = [method, path]
    if query:
        qs = "&".join(f"{k}={v}" for k, v in sorted(query.items()))
        parts.append(qs)
    if body:
        parts.append(json.dumps(body, separators=(",", ":")))
    y = "#" + "#".join(parts)

    original = x + y
    signature = hmac.new(
        API_SECRET.encode("utf-8"),
        original.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    headers["validate-signature"] = signature
    return headers


# ─── 3. Test balance ───
print("Testing GET /v4/balances with recvwindow=60000...")
path = "/v4/balances"
headers = sign("GET", path)
url = f"{BASE_URL}{path}"

print(f"  timestamp:   {headers['validate-timestamp']}")
print(f"  recvwindow:  {headers['validate-recvwindow']}")
print(f"  signature:   {headers['validate-signature'][:16]}...")
print()

req = urllib.request.Request(
    url,
    headers={**headers, "User-Agent": "PhoenixGenesis/1.0", "Content-Type": "application/json"},
    method="GET",
)

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        print(f"HTTP 200")
        print(f"rc: {data.get('rc')}")
        print(f"mc: {data.get('mc')}")
        if data.get("rc") == 0:
            print()
            print(">>> SUCCESS! Auth working.")
            result = data.get("result", {})
            assets = result.get("assets", [])
            print(f"  assets count: {len(assets)}")
            for a in assets[:5]:
                print(f"    {a.get('currency')}: total={a.get('totalAmount')} "
                      f"available={a.get('availableAmount')}")
        else:
            print()
            print(f">>> Still failing: {data.get('mc')}")
            print(f"Full response: {json.dumps(data, indent=2)[:400]}")
except urllib.error.HTTPError as e:
    body = e.read().decode()[:400]
    print(f"HTTP {e.code}: {body}")
except Exception as e:
    print(f"Error: {e}")