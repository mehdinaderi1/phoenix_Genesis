import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exchanges.xt_exchange import XTExchange
spot = XTExchange(timeout=20)
for sym in ["ADAUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT"]:
    try:
        c = spot.get_historical_candles(sym, "4H", limit=1000)
        if c:
            path = f"data/historical/{sym}_4H.csv"
            with open(path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["timestamp","open","high","low","close","volume"])
                for x in c:
                    w.writerow([x["timestamp"], x["open"], x["high"], x["low"], x["close"], x["volume"]])
            print(f"{sym}: {len(c)} candles")
        else:
            print(f"{sym}: EMPTY")
    except Exception as e:
        print(f"{sym}: ERROR {type(e).__name__}")
