import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.futures_wrapper_v2 import XTFuturesExchange

w = XTFuturesExchange(dry_run=False, extra_skip=["btc_usdt", "eth_usdt"])

fet = None
for p in w.get_user_positions():
    if p.get("symbol") == "fet_usdt":
        fet = p
        break

if not fet:
    print("No FET position - clean")
else:
    side = fet.get("positionSide")
    size = int(float(fet.get("positionSize", 0)))
    close_side = "BUY" if side == "SHORT" else "SELL"
    
    print(f"Closing FET {side} size={size}")
    ok, resp = w.place_order(
        symbol="fet_usdt",
        side=close_side,
        position_side=side,
        contracts=size,
        leverage=10,
    )
    print(f"Response: {json.dumps(resp, indent=2)[:300]}")
    
    time.sleep(5)
    remaining = [p for p in w.get_user_positions() if p.get("symbol") == "fet_usdt"]
    if remaining:
        print(f"! Still open: {remaining[0].get('positionSize')} - close manually")
    else:
        print("FET closed cleanly")
