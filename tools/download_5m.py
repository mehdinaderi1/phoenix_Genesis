"""Download 5m data for scalper backtest."""
import sys, os, csv, time, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exchanges.xt_exchange import XTExchange

SYMBOLS = ["ETHUSDT","OPUSDT","DOGEUSDT","PEPEUSDT","AAVEUSDT","INJUSDT",
           "FETUSDT","WLDUSDT","ZECUSDT","XRPUSDT","DASHUSDT"]
TF = "5m"
BATCH = 1000
SLEEP = 0.25

def download_paginated(spot, sym, target_candles):
    all_rows = []
    end_ts = int(time.time() * 1000)
    # 5m = 12 candles/hour, target/12 hours back
    start_boundary = end_ts - int(target_candles / 12 * 3600 * 1000 * 1.5)
    while len(all_rows) < target_candles and end_ts > start_boundary:
        try:
            batch = spot.get_historical_candles(sym, TF, limit=BATCH,
                                                startTime=start_boundary, endTime=end_ts)
        except Exception as e:
            return None, f"fetch: {type(e).__name__}: {str(e)[:60]}"
        if not batch:
            break
        rows = []
        for c in batch:
            ts = c.get("timestamp", 0)
            rows.append((ts, c.get("open"), c.get("high"), c.get("low"),
                         c.get("close"), c.get("volume")))
        rows = [r for r in rows if r[0] and r[4]]
        if not rows:
            break
        all_rows = rows + all_rows
        oldest = min(r[0] for r in rows)
        oldest_ms = oldest * 1000 if oldest < 10**12 else oldest
        end_ts = oldest_ms - 1
        time.sleep(SLEEP)
    # dedupe
    seen = set(); deduped = []
    for r in all_rows:
        if r[0] not in seen:
            seen.add(r[0]); deduped.append(r)
    deduped.sort(key=lambda x: x[0])
    if len(deduped) > target_candles:
        deduped = deduped[-target_candles:]
    if not deduped:
        return None, "empty"
    return deduped, "ok"

def main(days=30):
    os.makedirs("data/historical", exist_ok=True)
    spot = XTExchange(timeout=20)
    target = days * 24 * 12  # 5m candles per day = 288
    print(f"[5m] {len(SYMBOLS)} symbols × {target} candles ({days}d)\n")
    ok, fail = 0, 0
    for sym in SYMBOLS:
        rows, reason = download_paginated(spot, sym, target)
        if rows is None:
            print(f"[FAIL] {sym}: {reason}"); fail += 1; continue
        path = f"data/historical/{sym}_{TF}.csv"
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["timestamp","open","high","low","close","volume"])
            w.writerows(rows)
        print(f"[OK] {sym}: {len(rows)} candles -> {path}")
        ok += 1
    print(f"\n[Done] {ok} ok, {fail} failed")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    main(days=ap.parse_args().days)