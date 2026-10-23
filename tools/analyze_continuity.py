"""
Diagnose candle continuity — is the existing data usable for RSI?
"""
import sqlite3
from pathlib import Path

DB = Path("data/phoenix.db")


def main():
    conn = sqlite3.connect(str(DB))
    rows = conn.execute(
        "SELECT timestamp FROM market_candles "
        "WHERE symbol='BTCUSDT' AND timeframe='5m' "
        "ORDER BY timestamp ASC"
    ).fetchall()
    conn.close()

    if not rows:
        print("No candles.")
        return

    timestamps = [r[0] for r in rows]
    print(f"Total candles: {len(timestamps)}")
    print(f"First: {timestamps[0]}")
    print(f"Last:  {timestamps[-1]}")
    span = (timestamps[-1] - timestamps[0]) / 86400.0
    print(f"Span: {span:.1f} days")
    print()

    # Find gaps (expected gap: 300 sec for 5m)
    expected_delta = 300
    gaps = []
    for i in range(1, len(timestamps)):
        delta = timestamps[i] - timestamps[i - 1]
        if delta > expected_delta + 30:  # > 5m30s
            gaps.append((timestamps[i - 1], timestamps[i], delta))

    print(f"Gaps (>5m30s): {len(gaps)}")
    if gaps:
        gap_sizes = sorted([g[2] / 3600 for g in gaps], reverse=True)
        print(f"  Largest 5 gaps (hours): {[round(x, 1) for x in gap_sizes[:5]]}")
        print(f"  Median gap (hours): {sorted(gap_sizes)[len(gap_sizes)//2]:.1f}")
        total_gap_hours = sum(gap_sizes)
        print(f"  Total gap time: {total_gap_hours:.1f} hours")
        continuous_hours = span * 24 - total_gap_hours
        print(f"  Continuous time: {continuous_hours:.1f} hours ({continuous_hours/24:.1f} days)")
    print()

    # Continuous stretches
    stretches = []
    current_start = timestamps[0]
    current_len = 1
    for i in range(1, len(timestamps)):
        delta = timestamps[i] - timestamps[i - 1]
        if delta <= expected_delta + 30:
            current_len += 1
        else:
            stretches.append((current_start, timestamps[i-1], current_len))
            current_start = timestamps[i]
            current_len = 1
    stretches.append((current_start, timestamps[-1], current_len))

    stretches.sort(key=lambda x: x[2], reverse=True)
    print(f"Continuous stretches: {len(stretches)}")
    print(f"  Top 10 by length:")
    for start, end, length in stretches[:10]:
        duration_hours = (end - start) / 3600
        print(f"    {length:>4} candles ({duration_hours:>5.1f}h)  "
              f"from {start} to {end}")
    print()

    # RSI needs >= 200 continuous for EMA200 trend filter, or >= 50 without
    usable_200 = sum(1 for s in stretches if s[2] >= 200)
    usable_50 = sum(1 for s in stretches if s[2] >= 50)
    usable_20 = sum(1 for s in stretches if s[2] >= 20)
    print("Usability for RSI backtest:")
    print(f"  Stretches >= 200 candles (with trend filter): {usable_200}")
    print(f"  Stretches >= 50  candles (RSI + ATR only):     {usable_50}")
    print(f"  Stretches >= 20  candles (bare RSI):           {usable_20}")
    print()

    if usable_50 >= 20:
        print(">>> Data is SEGMENTED but usable.")
        print(">>> We can backtest per-stretch (RSI resets at each gap).")
    elif usable_50 >= 5:
        print(">>> Data is limited. Backtest will be indicative only.")
    else:
        print(">>> Data is too fragmented. MUST fetch more from XT.")


if __name__ == "__main__":
    main()