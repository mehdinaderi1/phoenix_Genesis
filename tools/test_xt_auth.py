import os, time, hmac, hashlib, json, urllib.request, urllib.error
from datetime import datetime

API_KEY = os.environ.get("XT_API_KEY", "")
API_SECRET = os.environ.get("XT_API_SECRET", "")
BASE_URL = "https://fapi.xt.com"

def sign_v1(method, path, query, body):
    s = method + path
    if query:
        s += "?" + query
    s += body
    return hmac.new(API_SECRET.encode(), s.encode(), hashlib.sha256).hexdigest()

def sign_v2(method, path, query, body):
    s = method + path + query + body
    return hmac.new(API_SECRET.encode(), s.encode(), hashlib.sha256).hexdigest()

def sign_v3(method, path, query, body):
    s = method + path
    if query:
        s += "?" + query
    if body:
        s += "&" + body
    return hmac.new(API_SECRET.encode(), s.encode(), hashlib.sha256).hexdigest()

def auth_request(method, path, query="", body="", sign_func=sign_v1):
    ts = str(int(time.time() * 1000))
    sig = sign_func(method, path, query, body)
    url = BASE_URL + path
    if query:
        url += "?" + query
    req = urllib.request.Request(url, method=method)
    req.add_header("validate-appkey", API_KEY)
    req.add_header("validate-timestamp", ts)
    req.add_header("validate-signature", sig)
    req.add_header("validate-algorithms", "HmacSHA256")
    req.add_header("validate-recvwindow", "5000")
    req.add_header("Content-Type", "application/json")
    if body:
        req.data = body.encode()
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return {"ok": True, "status": r.status, "body": r.read().decode()}
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "body": e.read().decode()}
    except Exception as e:
        return {"ok": False, "status": 0, "body": str(e)}

def try_endpoints():
    print("=" * 70)
    print("XT Futures Auth Test  |", datetime.now().isoformat())
    print("=" * 70)
    print(f"API_KEY: {len(API_KEY)} chars, API_SECRET: {len(API_SECRET)} chars")
    print()

    endpoints = [
        ("GET", "/future/user/v1/account/list", "", ""),
        ("GET", "/future/user/v1/position/list", "", ""),
        ("GET", "/future/user/v1/balance", "", ""),
    ]

    sign_funcs = [("v1", sign_v1), ("v2", sign_v2), ("v3", sign_v3)]

    for method, path, query, body in endpoints:
        print(f"--- {method} {path} ---")
        for name, fn in sign_funcs:
            r = auth_request(method, path, query, body, fn)
            print(f"  sig-{name}: status={r['status']}  body={r['body'][:200]}")
            if r["ok"]:
                print(f"  >>> SUCCESS with sig-{name}! <<<")
                try:
                    print(f"  JSON: {json.dumps(json.loads(r['body']), indent=2)[:600]}")
                except:
                    pass
                return name
        print()

    print("All signature variants failed. Possible causes:")
    print("  - API key not for Futures (check permissions in XT panel)")
    print("  - Wrong signature formula (need to check XT docs)")
    print("  - IP not whitelisted")
    return None

if __name__ == "__main__":
    if not API_KEY or not API_SECRET:
        print("ERROR: XT_API_KEY or XT_API_SECRET not set")
        print("Run: . .\\env.local.ps1 first")
    else:
        try_endpoints()
