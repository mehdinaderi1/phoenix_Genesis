import os, sys, hmac, hashlib, time, json
import urllib.request
from pathlib import Path

BASE_URL = "https://sapi.xt.com"
API_KEY = os.getenv("XT_API_KEY")
API_SECRET = os.getenv("XT_API_SECRET")

def get_server_time():
    req = urllib.request.Request(f"{BASE_URL}/v4/public/time", headers={"User-Agent": "PhoenixGenesis/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())["result"]["serverTime"]

server_t = get_server_time()
offset_ms = server_t - int(time.time() * 1000)

def sign(method, path, recv_window=60000):
    timestamp = str(int(time.time() * 1000) + offset_ms)
    h = {"validate-algorithms": "HmacSHA256", "validate-appkey": API_KEY,
         "validate-recvwindow": str(recv_window), "validate-timestamp": timestamp}
    x = "&".join(f"{k}={v}" for k, v in sorted(h.items()))
    y = f"#{method}#{path}"
    sig = hmac.new(API_SECRET.encode(), (x+y).encode(), hashlib.sha256).hexdigest()
    h["validate-signature"] = sig
    return h

headers = sign("GET", "/v4/balances")
req = urllib.request.Request(f"{BASE_URL}/v4/balances",
    headers={**headers, "User-Agent": "PhoenixGenesis/1.0"})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode())

print(f"rc: {data.get('rc')}, mc: {data.get('mc')}")
print()
print("All balances with total > 0:")
for a in data["result"]["assets"]:
    total = float(a.get("totalAmount", 0))
    if total > 0:
        print(f"  {a['currency']:>6}: total={total:.8f}  available={a.get('availableAmount')}")