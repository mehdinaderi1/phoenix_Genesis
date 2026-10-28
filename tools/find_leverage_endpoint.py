import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.futures_wrapper_v2 import XTFuturesExchange

w = XTFuturesExchange(dry_run=True)

# از مستندات XT: leverage معمولاً با POST set می‌شود
# باید test کنیم کدام مسیر جواب می‌دهد

paths = [
    # Most likely endpoints based on XT docs pattern
    ("POST", "/future/user/v1/position/leverage",  "symbol=fet_usdt&leverage=10"),
    ("POST", "/future/user/v1/leverage",           "symbol=fet_usdt&leverage=10"),
    ("POST", "/future/trade/v1/leverage",          "symbol=fet_usdt&leverage=10"),
    ("POST", "/future/trade/v1/order/leverage",    "symbol=fet_usdt&leverage=10"),
    ("POST", "/future/trade/v1/position/leverage", "symbol=fet_usdt&leverage=10"),
    ("POST", "/future/user/v1/position/set-leverage", "symbol=fet_usdt&leverage=10"),
    ("POST", "/future/trade/v1/position/leverage/set", "symbol=fet_usdt&leverage=10"),
    ("PUT",  "/future/user/v1/position/leverage",  "symbol=fet_usdt&leverage=10"),

    # Also check "init leverage" / "margin mode"
    ("POST", "/future/user/v1/position/margin-mode", "symbol=fet_usdt&marginMode=ISOLATED"),
    ("POST", "/future/trade/v1/position/margin-mode", "symbol=fet_usdt&marginMode=ISOLATED"),
]

print("Finding leverage endpoint...\n")
for m, p, b in paths:
    ok, data = w._request(m, p, body=b)
    status = "?"
    if isinstance(data, dict):
        rc = data.get("returnCode") if "returnCode" in data else data.get("rc")
        if rc == 0:
            status = "★ WORKS"
        elif data.get("status") == 404:
            status = "✗ 404"
        else:
            status = f"? rc={rc} msg={data.get('msgInfo', data.get('error', ''))}"
    print(f"  {m:4s} {p:50s} → {status}")
    if status.startswith("★"):
        print(f"       {json.dumps(data, indent=2)[:200]}")
