import os, time, hmac, hashlib, json, urllib.request, urllib.error

API_KEY = os.environ.get("XT_API_KEY", "")
API_SECRET = os.environ.get("XT_API_SECRET", "")
BASE_URL = "https://fapi.xt.com"

def sign(method, path, query="", body=""):
    ts = str(int(time.time() * 1000))
    fixed = f"validate-appkey={API_KEY}&validate-timestamp={ts}"
    if query:
        unenc = f"{fixed}#{path}#{query}"
    elif body:
        unenc = f"{fixed}#{path}#{body}"
    else:
        unenc = f"{fixed}#{path}"
    return ts, hmac.new(API_SECRET.encode(), unenc.encode(), hashlib.sha256).hexdigest()

def try_ep(method, path, query="", body=""):
    ts, sig = sign(method, path, query, body)
    url = BASE_URL + path + ("?" + query if query else "")
    req = urllib.request.Request(url, method=method)
    req.add_header("validate-appkey", API_KEY)
    req.add_header("validate-timestamp", ts)
    req.add_header("validate-signature", sig)
    req.add_header("validate-algorithms", "HmacSHA256")
    req.add_header("validate-recvwindow", "10000")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    if body:
        req.data = body.encode()
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return True, r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return False, e.code, e.read().decode()
    except Exception as e:
        return False, 0, str(e)

probes = [
    # Leverage variations
    ("POST", "/future/user/v1/position/leverage", "symbol=fet_usdt&leverage=10"),
    ("POST", "/future/trade/v1/order/leverage", "symbol=fet_usdt&leverage=10"),
    ("POST", "/future/user/v1/leverage", "symbol=fet_usdt&leverage=10"),
    ("POST", "/future/user/v1/position/leverage/set", "symbol=fet_usdt&leverage=10"),
    ("GET", "/future/user/v1/position/leverage", "symbol=fet_usdt"),

    # SL/TP variations
    ("POST", "/future/trade/v1/order/sl-tp", "symbol=fet_usdt&sl=0.18&tp=0.19"),
    ("POST", "/future/trade/v1/position/sl-tp/create", "symbol=fet_usdt"),
    ("POST", "/future/trade/v1/position/set-sl-tp", "symbol=fet_usdt"),
    ("POST", "/future/user/v1/position/sl-tp", "symbol=fet_usdt"),

    # Close position variations
    ("POST", "/future/trade/v1/position/close-all", "symbol=fet_usdt"),
    ("POST", "/future/trade/v1/order/close", "symbol=fet_usdt"),
    ("POST", "/future/trade/v1/position/close", "symbol=fet_usdt&positionSide=LONG"),
    ("POST", "/future/trade/v1/position/close", "symbol=fet_usdt&side=SELL&positionSide=LONG&type=MARKET&size=10"),

    # Order create with positionSide (won't place real order - will fail validation)
    ("POST", "/future/trade/v1/order/create", "symbol=fet_usdt&side=BUY&positionSide=LONG&type=LIMIT&size=10&price=0.0001&timeInForce=GTC"),
]

print("Extended probe for leverage/SL-TP/close...\n")
for m, p, b in probes:
    ok, st, resp = try_ep(m, p, "", b)
    marker = "★" if st == 200 and "invalid" not in resp.lower() else ("·" if st in (200, 400, 403) else " ")
    print(f"{marker} {m:4s} {p:48s}  status={st}")
    print(f"   {resp[:200]}")
    print()
