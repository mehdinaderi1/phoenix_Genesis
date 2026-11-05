import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exchanges.xt_exchange import XTExchange
import csv, time

SYMBOLS = ["ETHUSDT","OPUSDT","DOGEUSDT","PEPEUSDT","AAVEUSDT","INJUSDT",
           "FETUSDT","WLDUSDT","ZECUSDT","XRPUSDT","DASHUSDT"]
spot = XTExchange(timeout=20)
for sym in SYMBOLS:
    c = spot.get_historical_candles(sym, "15m", limit=1000)
    # paginate 3 times to get 30 days (2880 candles)
    all_c = c if c else []
    for _ in range(2):
        if not all_c: break
        oldest = min(x["timestamp"] for x in all_c)
        oldest_ms = oldest * 1000 if oldest < 10**12 else oldest
        batch = spot.get_historical_candles(sym, "15m", limit=1000, endTime=oldest_ms - 1)
        if not batch: break
        all_c = batch + all_c
        time.sleep(0.3)
    if not all_c:
        print(f"{sym}: EMPTY"); continue
    path = f"data/historical/{sym}_15m.csv"
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp","open","high","low","close","volume"])
        for x in all_c:
            w.writerow([x["timestamp"],x["open"],x["high"],x["low"],x["close"],x["volume"]])
    print(f"{sym}: {len(all_c)} candles")
