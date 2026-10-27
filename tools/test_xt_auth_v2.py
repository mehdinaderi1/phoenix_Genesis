import os, time, hmac, hashlib, json, urllib.request, urllib.error

API_KEY = os.environ.get("XT_API_KEY", "")
API_SECRET = os.environ.get("XT_API_SECRET", "")
BASE_URL = "https://fapi.xt.com"

def get_server_time_offset():
    """Get time offset between local and server."""
    try:
        req = urllib.request.Request(BASE_URL + "/future/market/v1/public/q/ticker?symbol=btc_usdt")
        r = urllib.request.urlopen(req, timeout=10)
        data = json.loads(r.read())
        # XT sometimes returns timestamp in header, sometimes in body
        # Fallback: use Date header
        server_ts = r.headers.get("Date")
        if server_ts:
            from email.utils import parsedate_to_datetime
            server_time = parsedate_to_datetime(server_ts).timestamp() * 1000
            local_time = time.time() * 1000
            return int(server_time - local_time)
    except Exception as e:
        print(f"Could not get server time: {e}")
    return 0

def sign_futures(method, path, query="", body=""):
    """Correct XT Futures signature: fixed_header#endpoint#query_or_body"""
    timestamp = str(int(time.time() * 1000))
    fixed_header = f"validate-appkey={API_KEY}&validate-timestamp={timestamp}"
    if query:
        unencrypted = f"{fixed_header}#{path}#{query}"
    elif body:
        unencrypted = f"{fixed_header}#{path}#{body}"
    else:
        unencrypted = f"{fixed_header}#{path}"
    signature = hmac.new(API_SECRET.encode(), unencrypted.encode(), hashlib.sha256).hexdigest()
    return timestamp, signature

def try_endpoint(method, path, query="", body=""):
    ts, sig = sign_futures(method, path, query, body)
    url = BASE_URL + path
    if query:
        url += "?" + query
    req = urllib.request.Request(url, method=method)
    req.add_header("validate-appkey", API_KEY)
    req.add_header("validate-timestamp", ts)
    req.add_header("validate-signature", sig)
    req.add_header("validate-algorithms", "HmacSHA256")
    req.add_header("validate-recvwindow", "10000")  # 10s to allow clock skew
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

if __name__ == "__main__":
    print("XT Futures Auth Test v2")
    offset = get_server_time_offset()
    print(f"Server time offset: {offset} ms")
    if abs(offset) > 2000:
        print("WARNING: Local clock is far from server. Run: w32tm /resync")

    endpoints = [
        ("GET", "/future/user/v1/account/list", "", ""),
        ("GET", "/future/user/v1/position/list", "", ""),
    ]
    for method, path, query, body in endpoints:
        ok, status, resp = try_endpoint(method, path, query, body)
        print(f"\n--- {path} ---")
        print(f"Status: {status}")
        print(f"Response: {resp[:300]}")
        if ok:
            print(">>> SUCCESS <<<")