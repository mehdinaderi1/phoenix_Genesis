import os, time, hmac, hashlib, json, urllib.request, urllib.error

API_KEY = os.environ.get("XT_API_KEY", "")
API_SECRET = os.environ.get("XT_API_SECRET", "")
BASE_URL = "https://fapi.xt.com"

def sign(method, path, query=""):
    ts = str(int(time.time() * 1000))
    fixed = f"validate-appkey={API_KEY}&validate-timestamp={ts}"
    unenc = f"{fixed}#{path}#{query}" if query else f"{fixed}#{path}"
    return ts, hmac.new(API_SECRET.encode(), unenc.encode(), hashlib.sha256).hexdigest()

def try_ep(method, path, query=""):
    ts, sig = sign(method, path, query)
    url = BASE_URL + path + ("?" + query if query else "")
    req = urllib.request.Request(url, method=method)
    req.add_header("validate-appkey", API_KEY)
    req.add_header("validate-timestamp", ts)
    req.add_header("validate-signature", sig)
    req.add_header("validate-algorithms", "HmacSHA256")
    req.add_header("validate-recvwindow", "10000")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return True, r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return False, e.code, e.read().decode()
    except Exception as e:
        return False, 0, str(e)

# Path candidates
paths = [
    "/future/user/v1/account/balances",
    "/future/user/v1/account/asset",
    "/future/user/v1/account/margin",
    "/future/user/v1/account/portfolio",
    "/future/user/v1/account/equity",
    "/future/user/v1/account/funds",
    "/future/user/v1/account/available",
    "/future/user/v1/account/summary",
    "/future/user/v1/account/overview",
    "/future/user/v1/position/balance",
    "/future/user/v1/wallet/balance",
    "/future/user/v1/asset",
    "/future/user/v1/assets",
    "/future/user/v1/fund/list",
    "/future/trade/v1/account/info",
]

# Also try with query params on account/info
paths_with_query = [
    ("/future/user/v1/account/info", "include=balance"),
    ("/future/user/v1/account/info", "detail=full"),
    ("/future/user/v1/account/info", "fields=balance,equity"),
]

print("Testing balance endpoints...\n")
found = None

for p in paths:
    ok, st, resp = try_ep("GET", p)
    marker = "★" if ok else " "
    print(f"{marker} {p:48s} status={st}")
    if ok:
        print(f"   >>> {resp[:300]}")
        found = p
        break

if not found:
    print("\nTrying query params on account/info...")
    for p, q in paths_with_query:
        ok, st, resp = try_ep("GET", p, q)
        marker = "★" if ok else " "
        print(f"{marker} {p}?{q:30s} status={st}")
        if ok:
            print(f"   >>> {resp[:300]}")
            found = f"{p}?{q}"
            break

if found:
    print(f"\n✓ WORKING: {found}")
else:
    print("\n✗ Balance endpoint not found")
    print("Falling back: use position list to infer capital")
    print("Or query XT docs at https://doc.xt.com/")
