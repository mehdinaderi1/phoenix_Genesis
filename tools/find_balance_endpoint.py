import os, time, hmac, hashlib, json, urllib.request, urllib.error

API_KEY = os.environ.get("XT_API_KEY", "")
API_SECRET = os.environ.get("XT_API_SECRET", "")
BASE_URL = "https://fapi.xt.com"

def sign_futures(method, path, query="", body=""):
    ts = str(int(time.time() * 1000))
    fixed = f"validate-appkey={API_KEY}&validate-timestamp={ts}"
    unenc = f"{fixed}#{path}#{query}" if query else (f"{fixed}#{path}#{body}" if body else f"{fixed}#{path}")
    sig = hmac.new(API_SECRET.encode(), unenc.encode(), hashlib.sha256).hexdigest()
    return ts, sig

def try_endpoint(method, path, query=""):
    ts, sig = sign_futures(method, path, query)
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

# Try common balance/account endpoints
endpoints = [
    "/future/user/v1/balance",
    "/future/user/v1/account/balance",
    "/future/user/v1/account/info",
    "/future/user/v1/account",
    "/future/user/v1/wallet",
    "/future/user/v1/asset/list",
    "/future/user/v1/account/detail",
    "/future/user/v1/account/fund",
]

for path in endpoints:
    ok, status, resp = try_endpoint("GET", path)
    marker = "★" if ok else " "
    print(f"{marker} {path:45s}  status={status}  {resp[:120]}")
    if ok:
        print(f"   >>> WORKING: {path} <<<")
        try:
            data = json.loads(resp)
            if data.get("result"):
                print(f"   Result sample: {json.dumps(data['result'][:1] if isinstance(data['result'], list) else data['result'], indent=2)[:400]}")
        except:
            pass
