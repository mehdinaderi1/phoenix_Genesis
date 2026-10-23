"""
Full paginated fetch from XT — target 30 days of 5m candles.
Format: {'t': ms, 'o': '...', 'h': '...', 'l': '...', 'c': '...', 'v': '...'}
"""
import sys
import time
import sqlite3
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from exchanges.xt_exchange import XTExchange

DB = Path("data/phoenix.db")
SYMBOL = "BTCUSDT"
TF = "5m"
BATCH = 500
MAX_BATCHES = 40  # 40 * 500 * 5min = ~139 days


def try_request(xt, params):
    try:
        r = xt._request("/v4/public/kline", params)
        result = r.get("result") or r.get("data") or []
        if isinstance(result, dict):
            result = result.get("list") or result.get("klines") or []
        return result or []
    except Exception as e:
        print(f"  request error: {e}")
        return []


def parse(c):
    """XT format -> (ts_sec, o, h, l, c, v_base)."""
    if not isinstance(c, dict):
        return None
    ts_ms = c.get("t")
    if ts_ms is None:
        return None
    try:
        return (
            int(ts_ms) // 1000,
            float(c["o"]),
            float(c["h"]),
            float(c["l"]),
            float(c["c"]),
            float(c.get("v", 0)),
        )
    except (KeyError, ValueError, TypeError):
        return None


def fetch_page(xt, end_ms=None, method="endTime"):
    """Fetch one page. Try endTime, then before, then from."""
    base = {
        "symbol": "btc_usdt",
        "interval": xt._normalize_interval(TF),
        "limit": BATCH,
    }
    if end_ms is None:
        return try_request(xt, base)
    if method == "endTime":
        return try_request(xt, {**base, "endTime": end_ms})
    if method == "before":
        return try_request(xt, {**base, "before": end_ms})
    if method == "from":
        return try_request(xt, {**base, "from": end_ms})
    return []


def discover_pagination(xt):
    """Find which pagination param works."""
    print("Discovering pagination...")
    page1 = try_request(xt, {
        "symbol": "btc_usdt",
        "interval": xt._normalize_interval(TF),
        "limit": BATCH,
    })
    if not page1:
        print("  Even initial fetch returned 0.")
        return None

    ts_first = sorted([int(c["t"]) for c in page1])
    oldest_ms = ts_first[0]
    print(f"  initial page: {len(page1)} items, oldest = {oldest_ms}")

    for method in ("endTime", "before", "from"):
        page2 = fetch_page(xt, oldest_ms - 1, method)
        if not page2:
            print(f"  {method}: 0 items")
            continue
        ts2 = sorted([int(c["t"]) for c in page2])
        if ts2[0] >= oldest_ms:
            print(f"  {method}: returned {len(page2)} but not older data (broken)")
            continue
        overlap = sum(1 for t in ts2 if t in ts_first)
        print(f"  {method}: {len(page2)} items, oldest = {ts2[0]}, overlap = {overlap}")
        if overlap == 0:
            return method
        if overlap < len(page2) // 2:
            return method  # partial overlap acceptable
    return None


def main():
    xt = XTExchange(timeout=20)

    method = discover_pagination(xt)
    if method is None:
        print()
        print("No working pagination method found.")
        print("Will fetch only the initial page (500 candles).")
        method = "none"

    print()
    print(f"Using pagination method: {method}")
    print()

    all_candles = []
    seen = set()
    end_ms = None

    for batch_num in range(1, MAX_BATCHES + 1):
        if method == "none":
            page = try_request(xt, {
                "symbol": "btc_usdt",
                "interval": xt._normalize_interval(TF),
                "limit": BATCH,
            })
        else:
            page = fetch_page(xt, end_ms, method)

        if not page:
            print(f"Batch {batch_num}: empty, stopping")
            break

        new_count = 0
        min_ts_ms = None
        for c in page:
            p = parse(c)
            if p is None:
                continue
            if p[0] in seen:
                continue
            seen.add(p[0])
            all_candles.append(p)
            new_count += 1
            ts_ms = int(c["t"])
            if min_ts_ms is None or ts_ms < min_ts_ms:
                min_ts_ms = ts_ms

        print(f"Batch {batch_num:>2}: {len(page):>3} items, "
              f"new={new_count:>3}, total={len(all_candles):>5}")

        if new_count == 0:
            print("  no new data, stopping")
            break
        if min_ts_ms is None:
            break

        end_ms = min_ts_ms - 1
        time.sleep(0.5)

        if method == "none":
            break

    if not all_candles:
        print("No candles fetched.")
        return

    # Insert into DB
    conn = sqlite3.connect(str(DB))
    inserted = 0
    for p in all_candles:
        try:
            conn.execute(
                "INSERT OR REPLACE INTO market_candles "
                "(symbol, timeframe, timestamp, open, high, low, close, volume) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (SYMBOL, TF, p[0], p[1], p[2], p[3], p[4], p[5])
            )
            inserted += 1
        except Exception as e:
            print(f"  insert error: {e}")
            break
    conn.commit()
    conn.close()
    print()
    print(f"Inserted {inserted} candles into {DB}")

    # Coverage check
    conn = sqlite3.connect(str(DB))
    row = conn.execute(
        "SELECT MIN(timestamp), MAX(timestamp), COUNT(*) FROM market_candles "
        "WHERE symbol='BTCUSDT' AND timeframe='5m'"
    ).fetchone()
    conn.close()

    if row and row[2] > 0:
        span_days = (row[1] - row[0]) / 86400.0
        expected = span_days * 24 * 12
        coverage = row[2] / expected * 100
        print(f"Coverage: {row[2]} / ~{int(expected)} = {coverage:.1f}%")
        print(f"  span: {span_days:.1f} days")
        print()
        if coverage >= 95:
            print(">>> Excellent! Data is continuous.")
        elif coverage >= 80:
            print(">>> Good, some small gaps.")
        elif coverage >= 50:
            print(">>> Usable, gaps will split backtest.")
        else:
            print(">>> Still fragmented, but better than before.")


if __name__ == "__main__":
    main()