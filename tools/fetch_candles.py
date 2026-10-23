"""
Fetch 1500 candles of 5m from XT and insert into DB.
Handles multiple response formats.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from exchanges.xt_exchange import XTExchange
import sqlite3

DB_PATH = Path("data/phoenix.db")
SYMBOL = "BTCUSDT"
TIMEFRAME = "5m"
TARGET = 1500


def fetch(xt, limit):
    return xt._request("/v4/public/kline", {
        "symbol": "btc_usdt",
        "interval": xt._normalize_interval(TIMEFRAME),
        "limit": limit,
    }).get("result") or []


def parse_candle(c):
    if isinstance(c, dict):
        ts = c.get("timestamp") or c.get("time") or c.get("ts") or c.get("t")
        o = c.get("open") or c.get("o")
        h = c.get("high") or c.get("h")
        l = c.get("low") or c.get("l")
        cl = c.get("close") or c.get("c")
        v = c.get("volume") or c.get("vol") or c.get("v") or 0
        if ts is not None and o is not None and cl is not None:
            return (int(ts), float(o), float(h), float(l), float(cl), float(v))
    elif isinstance(c, (list, tuple)) and len(c) >= 6:
        return (int(c[0]), float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5]))
    return None


def main():
    xt = XTExchange(timeout=15)
    print(f"Fetching {TARGET} candles of {TIMEFRAME}...")
    result = fetch(xt, TARGET)
    print(f"Received {len(result)} items")
    if result:
        print(f"Sample[0]: {result[0]}")
        print(f"Sample[-1]: {result[-1]}")

    parsed = []
    failed = 0
    for c in result:
        p = parse_candle(c)
        if p:
            parsed.append(p)
        else:
            failed += 1

    print(f"Parsed: {len(parsed)}, Failed: {failed}")
    if not parsed:
        print("Could not parse any candles. Show format above.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    inserted = 0
    for p in parsed:
        try:
            conn.execute(
                "INSERT OR REPLACE INTO market_candles "
                "(symbol, timeframe, timestamp, open, high, low, close, volume) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (SYMBOL, TIMEFRAME, p[0], p[1], p[2], p[3], p[4], p[5])
            )
            inserted += 1
        except Exception as e:
            print(f"Insert error: {e}")
            break
    conn.commit()
    conn.close()
    print(f"Inserted {inserted} candles into {DB_PATH}")

    # Check coverage
    cur = sqlite3.connect(str(DB_PATH)).execute(
        "SELECT MIN(timestamp), MAX(timestamp), COUNT(*) FROM market_candles "
        "WHERE symbol='BTCUSDT' AND timeframe='5m'"
    )
    row = cur.fetchone()
    if row and row[2] > 0:
        span_days = (row[1] - row[0]) / 86400.0
        expected = span_days * 24 * 12
        coverage = row[2] / expected * 100
        print(f"Coverage: {row[2]} / ~{int(expected)} = {coverage:.1f}%")
        print(f"  span: {span_days:.1f} days")


if __name__ == "__main__":
    main()