import urllib.request, json
# XT public fee endpoint (اگر وجود داشته باشد)
urls = [
    "https://fapi.xt.com/future/market/v1/public/q/feeRate",
    "https://fapi.xt.com/future/market/v1/public/q/exchangeInfo",
]
for u in urls:
    try:
        with urllib.request.urlopen(u, timeout=10) as r:
            data = json.loads(r.read())
            print(f"OK {u}")
            print(f"  keys: {list(data.keys())[:5]}")
    except Exception as e:
        print(f"FAIL {u}: {type(e).__name__}")
