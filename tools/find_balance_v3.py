import os, time, hmac, hashlib, json, urllib.request, urllib.error
from itertools import product

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

# Broader set of plausible paths
paths = [
    "/future/user/v1/account/wallet",
    "/future/user/v1/account/balance",
    "/future/user/v1/account/asset",
    "/future/user/v1/account/assets",
    "/future/user/v1/account/list",
    "/future/user/v1/wallet/list",
    "/future/user/v1/balances",
    "/future/user/v1/balance",
    "/future/user/v1/account/fund",
    "/future/user/v1/account/funds",
    "/future/user/v1/account/overview",
    "/future/user/v1/account/portfolio",
    "/future/user/v1/account/info/balance",
    "/future/user/v1/account/info/asset",
    "/future/user/v1/account/info/wallet",
    "/future/user/v1/account/info/margin",
]

print("Testing balance endpoint variations...\n")
found = None
for p in paths:
    ok, st, resp = try_ep("GET", p)
    if st in (200, 403):  # 403 means endpoint exists
        print(f"{'★' if st==200 else '·'} GET {p:50s} status={st}")
        print(f"   {resp[:250]}")
        if st == 200:
            found = p
            break
    else:
        print(f"  GET {p:50s} status={st}")

if not found:
    print("\nTrying with query params on /account/balances and /account/info...\n")
    paths_q = [
        ("/future/user/v1/account/balances", "coin=usdt"),
        ("/future/user/v1/account/balances", "asset=USDT"),
        ("/future/user/v1/account/balances", "currency=USDT"),
        ("/future/user/v1/account/info", "withBalance=true"),
        ("/future/user/v1/account/info", "includeAsset=true"),
        ("/future/user/v1/account/info", "detailed=true"),
    ]
    for p, q in paths_q:
        ok, st, resp = try_ep("GET", p, q)
        print(f"{'★' if ok else ' '} GET {p}?{q:20s} status={st}  {resp[:180]}")
        if ok and "balance" in resp.lower() or "usdt" in resp.lower():
            found = f"{p}?{q}"
            break

if found:
    print(f"\n✓ FOUND: {found}")
else:
    print("\n✗ No balance endpoint found in this round")
