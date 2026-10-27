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

tests = [
    ("GET", "/future/user/v1/account/balances", "", ""),
    ("POST", "/future/user/v1/account/balances", "", ""),
    ("POST", "/future/user/v1/account/balances", "", "{}"),
    ("GET", "/future/user/v1/account/balances", "coin=usdt", ""),
    ("POST", "/future/user/v1/account/asset/list", "", "{}"),
    ("POST", "/future/user/v1/asset/list", "", "{}"),
]

for m, p, q, b in tests:
    ok, st, resp = try_ep(m, p, q, b)
    marker = "★" if ok else " "
    print(f"{marker} {m:4s} {p:45s} q={q:10s} b={b:5s} status={st}")
    if ok:
        print(f"   >>> {resp[:250]}")
        print()
