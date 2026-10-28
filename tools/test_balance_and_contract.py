import os, time, hmac, hashlib, json, urllib.request, urllib.error

API_KEY = os.environ.get("XT_API_KEY", "")
API_SECRET = os.environ.get("XT_API_SECRET", "")
BASE_URL = "https://fapi.xt.com"

def sign(method, path, query="", body=""):
    ts = str(int(time.time() * 1000))
    fixed = f"validate-appkey={API_KEY}&validate-timestamp={ts}"
    unenc = f"{fixed}#{path}#{query}" if query else (f"{fixed}#{path}#{body}" if body else f"{fixed}#{path}")
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
    req.add_header("Content-Type", "application/json")
    if body:
        req.data = body.encode()
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return True, r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return False, e.code, e.read().decode()
    except Exception as e:
        return False, 0, str(e)

print("=== 1) Balance endpoint ===")
ok, st, resp = try_ep("GET", "/future/user/v1/compat/balance/list")
print(f"status={st}")
print(resp[:500])

print("\n=== 2) Contract info (FET) ===")
ok, st, resp = try_ep("GET", "/future/market/v1/public/symbol/detail", "symbol=fet_usdt")
print(f"status={st}")
print(resp[:500])

print("\n=== 3) Contract info (BNB) ===")
ok, st, resp = try_ep("GET", "/future/market/v1/public/symbol/detail", "symbol=bnb_usdt")
print(f"status={st}")
print(resp[:500])
