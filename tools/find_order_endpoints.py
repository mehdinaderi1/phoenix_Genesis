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

# Probe: place order, close, SL/TP, leverage
probes = [
    # Order placement
    ("POST", "/future/trade/v1/order/create", "", "symbol=fet_usdt&side=BUY&type=MARKET&size=10"),
    ("POST", "/future/trade/v1/order", "", "symbol=fet_usdt&side=BUY&type=MARKET&size=10"),
    ("POST", "/future/order/v1/create", "", "symbol=fet_usdt&side=BUY&type=MARKET&size=10"),
    
    # Leverage
    ("POST", "/future/user/v1/position/leverage", "", "symbol=fet_usdt&leverage=10"),
    ("POST", "/future/trade/v1/leverage", "", "symbol=fet_usdt&leverage=10"),
    
    # SL/TP
    ("POST", "/future/trade/v1/position/sl-tp", "", "symbol=fet_usdt&sl=0.18&tp=0.19"),
    ("POST", "/future/trade/v1/position/stop", "", "symbol=fet_usdt&sl=0.18"),
    
    # Open orders
    ("GET", "/future/trade/v1/order/list", "symbol=fet_usdt", ""),
    ("GET", "/future/user/v1/order/list", "symbol=fet_usdt", ""),
    
    # Position close
    ("POST", "/future/trade/v1/position/close", "", "symbol=fet_usdt"),
]

print("Testing order-related endpoints...\n")
for m, p, q, b in probes:
    ok, st, resp = try_ep(m, p, q, b)
    marker = "★" if st in (200, 400, 401, 403) and "Not Found" not in resp else " "
    print(f"{marker} {m:4s} {p:45s}  status={st}")
    print(f"   {resp[:220]}")
    print()
