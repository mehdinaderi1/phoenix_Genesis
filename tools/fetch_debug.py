"""
Fetch candles from XT in batches of 500, paginated.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from exchanges.xt_exchange import XTExchange
import sqlite3

DB = Path("data/phoenix.db")
SYMBOL = "BTCUSDT"
TF = "5m"
BATCH = 500


def try_request(xt, params):
    try:
        r = xt._request("/v4/public/kline", params)
        result = r.get("result") or r.get("data") or []
        if isinstance(result, dict):
            result = result.get("list") or result.get("klines") or []
        return result
    except Exception as e:
        print(f"  request error: {e}")
        return []


def main():
    xt = XTExchange(timeout=15)
    interval = xt._normalize_interval(TF)
    print(f"interval = {interval}")

    # Try limit=500
    print(f"Trying limit={BATCH}...")
    r = try_request(xt, {
        "symbol": "btc_usdt",
        "interval": interval,
        "limit": BATCH,
    })
    print(f"  got {len(r)} items")
    if r:
        print(f"  sample[0]: {r[0]}")
        print(f"  sample[-1]: {r[-1]}")

    if not r:
        print()
        print("Trying limit=100...")
        r = try_request(xt, {
            "symbol": "btc_usdt",
            "interval": interval,
            "limit": 100,
        })
        print(f"  got {len(r)} items")
        if r:
            print(f"  sample[0]: {r[0]}")

    if not r:
        print()
        print("Trying without limit...")
        r = try_request(xt, {
            "symbol": "btc_usdt",
            "interval": interval,
        })
        print(f"  got {len(r)} items")
        if r:
            print(f"  sample[0]: {r[0]}")

    if not r:
        print()
        print("All fetch attempts failed.")
        print("Need to inspect XTExchange._request and API signature.")
        return


if __name__ == "__main__":
    main()