import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exchanges.xt_exchange import XTExchange
spot = XTExchange(timeout=15)
for tf in ["5m", "15m", "1m"]:
    try:
        c = spot.get_historical_candles("BTCUSDT", tf, limit=100)
        n = len(c) if c else 0
        print(f"{tf:5s} -> {n:4d} candles")
        if c:
            print(f"       last ts: {c[-1].get('timestamp')}")
    except Exception as e:
        print(f"{tf:5s} -> ERROR: {type(e).__name__}: {str(e)[:60]}")
