"""
tools/download_historical.py — Download historical klines from XT (paginated)

Fetches up to N days of data by paginating backward in 800-candle batches.
Saves to data/historical/{SYMBOL}_{TF}.csv

Usage:
    python tools/download_historical.py
    python tools/download_historical.py --days 120
"""
import os, sys, time, argparse, csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exchanges.xt_exchange import XTExchange
from tools.futures_strategy_runner import SYMBOLS

OUT_DIR = "data/historical"
TIMEFRAMES = ["4H", "1H"]
BATCH_SIZE = 800          # سقف XT حدود 1000 است — 800 امن
RATE_LIMIT_SLEEP = 0.25   # rate limit: 10 req/s → 0.25s فاصله

CANDLES_PER_DAY = {
    "4H": 6,    # 24h / 4h
    "1H": 24,   # 24h / 1h
}


def _c(c, idx, key):
    if isinstance(c, dict):
        return c.get(key, 0)
    if isinstance(c, (list, tuple)) and len(c) > idx:
        return c[idx]
    return getattr(c, key, 0)


def _extract_row(c):
    return (
        _c(c, 0, "timestamp"),
        _c(c, 1, "open"),
        _c(c, 2, "high"),
        _c(c, 3, "low"),
        _c(c, 4, "close"),
        _c(c, 5, "volume"),
    )


def download_paginated(spot, sym, tf, target_candles):
    """Paginate backward via startTime/endTime."""
    all_rows = []
    end_ts = int(time.time() * 1000)
    start_boundary = end_ts - int(target_candles / CANDLES_PER_DAY[tf] * 86400 * 1000 * 1.5)

    while len(all_rows) < target_candles and end_ts > start_boundary:
        try:
            batch = spot.get_historical_candles(
                sym, tf,
                limit=BATCH_SIZE,
                startTime=start_boundary,
                endTime=end_ts,
            )
        except Exception as e:
            return None, f"fetch: {type(e).__name__}: {str(e)[:60]}"

        if not batch:
            break

        rows = [_extract_row(c) for c in batch]
        rows = [r for r in rows if r[0] and r[4]]
        if not rows:
            break

        all_rows = rows + all_rows
        oldest_ts = min(r[0] for r in rows)
        # XT returns timestamps in SECONDS; convert to MS for endTime
        oldest_ms = oldest_ts * 1000 if oldest_ts < 10**12 else oldest_ts
        end_ts = oldest_ms - 1

        time.sleep(RATE_LIMIT_SLEEP)

    # Dedupe by timestamp (in case batches overlap)
    seen = set()
    deduped = []
    for r in all_rows:
        if r[0] not in seen:
            seen.add(r[0])
            deduped.append(r)
    all_rows = deduped

    if len(all_rows) > target_candles:
        all_rows = all_rows[-target_candles:]

    if len(all_rows) > target_candles:
        all_rows = all_rows[-target_candles:]

    if not all_rows:
        return None, "empty (pagination yielded no data)"
    return all_rows, "ok"


def main(days=90):
    os.makedirs(OUT_DIR, exist_ok=True)
    spot = XTExchange(timeout=25)

    total = len(SYMBOLS) * len(TIMEFRAMES)
    done, failed = 0, []
    t0 = time.time()

    print(f"[DL] {len(SYMBOLS)} symbols × {len(TIMEFRAMES)} TFs = {total} downloads")
    print(f"[DL] target: ~{days} days per symbol")
    print(f"[DL] output: {os.path.abspath(OUT_DIR)}\n")

    for sym in SYMBOLS:
        for tf in TIMEFRAMES:
            target_candles = days * CANDLES_PER_DAY[tf]
            rows, reason = download_paginated(spot, sym, tf, target_candles)
            done += 1
            pct = done * 100 // total
            if rows is None:
                failed.append((sym, tf, reason))
                print(f"[{pct:3d}%] {sym:10s} {tf:3s}  FAIL: {reason}")
            else:
                path = os.path.join(OUT_DIR, f"{sym}_{tf}.csv")
                with open(path, "w", newline="") as f:
                    w = csv.writer(f)
                    w.writerow(["timestamp", "open", "high", "low", "close", "volume"])
                    w.writerows(rows)
                print(f"[{pct:3d}%] {sym:10s} {tf:3s}  {len(rows):5d} rows -> {path}")

    elapsed = time.time() - t0
    print(f"\n[Done] {done - len(failed)}/{total} ok, {len(failed)} failed, {elapsed:.1f}s")
    if failed:
        print("[Failed]:")
        for sym, tf, reason in failed:
            print(f"  {sym} {tf}: {reason}")

    files = [f for f in os.listdir(OUT_DIR) if f.endswith(".csv")]
    print(f"\n[Files] {len(files)} CSVs in {OUT_DIR}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=90, help="target days of history (default: 90)")
    args = ap.parse_args()
    main(days=args.days)