import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.futures_wrapper_v2 import XTFuturesExchange
w = XTFuturesExchange(dry_run=True)
for sym in ["btc_usdt", "eth_usdt", "hbar_usdt"]:
    ok, data = w._request("GET", "/future/market/v1/public/symbol/detail", f"symbol={sym}")
    if ok:
        r = data.get("result", {})
        print(f"{sym:12s} contractSize={r.get('contractSize')}  initLeverage={r.get('initLeverage')}")
