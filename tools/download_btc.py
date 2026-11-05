"""Download BTCUSDT 4H for backtest btc_direction."""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exchanges.xt_exchange import XTExchange

spot = XTExchange(timeout=20)
c = spot.get_historical_candles("BTCUSDT", "4H", limit=1000)
if not c:
    print("ERROR: 0 candles returned"); sys.exit(1)

path = "data/historical/BTCUSDT_4H.csv"
with open(path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["timestamp", "open", "high", "low", "close", "volume"])
    for x in c:
        w.writerow([x["timestamp"], x["open"], x["high"], x["low"], x["close"], x["volume"]])
print(f"BTCUSDT -> {len(c)} candles -> {path}")