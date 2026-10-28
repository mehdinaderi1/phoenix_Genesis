import sys, os, json, hmac, hashlib, time, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.futures_wrapper_v2 import XTFuturesExchange

w = XTFuturesExchange(dry_run=True)

def raw_post(path, body, content_type):
    """Send raw POST with custom Content-Type."""
    ts = str(int(time.time() * 1000))
    fixed = f"validate-appkey={w.api_key}&validate-timestamp={ts}"
    unenc = f"{fixed}#{path}#{body}"
    sig = hmac.new(w.api_secret.encode(), unenc.encode(), hashlib.sha256).hexdigest()
    
    url = w.BASE_URL + path
    req = urllib.request.Request(url, method="POST")
    req.add_header("validate-appkey", w.api_key)
    req.add_header("validate-timestamp", ts)
    req.add_header("validate-signature", sig)
    req.add_header("validate-algorithms", "HmacSHA256")
    req.add_header("validate-recvwindow", "10000")
    req.add_header("Content-Type", content_type)
    req.data = body.encode()
    
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

body_form = "symbol=fet_usdt&positionSide=SHORT&leverage=10"
body_json = '{"symbol":"fet_usdt","positionSide":"SHORT","leverage":10}'

print("=== A) URL-encoded body + form Content-Type ===")
status, resp = raw_post(
    "/future/user/v1/position/adjust-leverage",
    body_form,
    "application/x-www-form-urlencoded"
)
print(f"status={status}")
print(json.dumps(resp, indent=2)[:400])

print("\n=== B) JSON body + JSON Content-Type ===")
status, resp = raw_post(
    "/future/user/v1/position/adjust-leverage",
    body_json,
    "application/json"
)
print(f"status={status}")
print(json.dumps(resp, indent=2)[:400])

print("\n=== C) Verify current leverage ===")
ok, data = w._request("GET", "/future/trade/v1/position/leverage/list", "symbol=fet_usdt")
print(json.dumps(data, indent=2)[:300])
