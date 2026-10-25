#!/usr/bin/env python3
"""
Volatility vs Performance Analysis

For each session:
- Compute price range (max - min) / avg_price * 100
- Compute win rate and PnL
- Bin sessions by volatility range

Usage:
    python tools/volatility_analysis.py data/paper_sessions/*.json
"""
import json
import sys
from pathlib import Path
from collections import defaultdict


def analyze_session(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return None

    cycles = data.get("cycles", [])
    if not cycles:
        return None

    prices = [c.get("price") for c in cycles if c.get("price")]
    if len(prices) < 10:
        return None

    pmin, pmax = min(prices), max(prices)
    pavg = sum(prices) / len(prices)
    range_pct = (pmax - pmin) / pavg * 100 if pavg > 0 else 0

    wins = 0
    losses = 0
    total_pnl = 0.0
    trade_count = 0

    for c in cycles:
        action = c.get("action")
        pnl = c.get("realized_pnl", 0) or 0
        if action in ("CLOSE", "RECOVERY_CLOSE"):
            trade_count += 1
            if pnl > 0:
                wins += 1
            elif pnl < 0:
                losses += 1
            total_pnl += pnl
        elif action == "PARTIAL":
            total_pnl += pnl

    if trade_count == 0:
        return None

    return {
        "file": Path(path).name,
        "cycles": len(cycles),
        "price_range_pct": range_pct,
        "price_min": pmin,
        "price_max": pmax,
        "trades": trade_count,
        "wins": wins,
        "losses": losses,
        "win_pct": wins / trade_count * 100 if trade_count > 0 else 0,
        "total_pnl": total_pnl,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/volatility_analysis.py data/paper_sessions/*.json")
        sys.exit(1)

    sessions = []
    for path in sys.argv[1:]:
        result = analyze_session(path)
        if result:
            sessions.append(result)

    if not sessions:
        print("No sessions with trades found")
        return

    print(f"\nFound {len(sessions)} sessions with trades\n")

    # Sort by volatility
    sessions.sort(key=lambda s: s["price_range_pct"])

    # Print all
    print(f"{'Range%':>8} {'Trades':>7} {'Win%':>7} {'PnL':>10}  {'File'}")
    print("-" * 80)
    for s in sessions:
        print(f"{s['price_range_pct']:>7.3f}% {s['trades']:>7} "
              f"{s['win_pct']:>6.1f}% {s['total_pnl']:>+10.4f}  {s['file'][:16]}")

    # Bin analysis
    print("\n" + "=" * 80)
    print("VOLATILITY BINS")
    print("=" * 80)

    bins = [
        (0.0, 0.3, "TIGHT   (<0.3%)"),
        (0.3, 0.7, "NORMAL  (0.3-0.7%)"),
        (0.7, 1.5, "WIDE    (0.7-1.5%)"),
        (1.5, 99,  "EXTREME (>1.5%)"),
    ]

    for lo, hi, label in bins:
        in_bin = [s for s in sessions if lo <= s["price_range_pct"] < hi]
        if not in_bin:
            print(f"\n{label}: no sessions")
            continue

        total_trades = sum(s["trades"] for s in in_bin)
        total_wins = sum(s["wins"] for s in in_bin)
        total_pnl = sum(s["total_pnl"] for s in in_bin)
        win_pct = total_wins / total_trades * 100 if total_trades > 0 else 0

        print(f"\n{label}")
        print(f"  Sessions: {len(in_bin)}")
        print(f"  Trades:   {total_trades}")
        print(f"  Win rate: {win_pct:.1f}%")
        print(f"  PnL:      {total_pnl:+.4f}")

    # Correlation
    print("\n" + "=" * 80)
    print("CORRELATION (range% vs win%)")
    print("=" * 80)
    if len(sessions) >= 3:
        n = len(sessions)
        ranges = [s["price_range_pct"] for s in sessions]
        win_pcts = [s["win_pct"] for s in sessions]

        mean_r = sum(ranges) / n
        mean_w = sum(win_pcts) / n
        cov = sum((ranges[i] - mean_r) * (win_pcts[i] - mean_w) for i in range(n)) / n
        var_r = sum((r - mean_r) ** 2 for r in ranges) / n
        var_w = sum((w - mean_w) ** 2 for w in win_pcts) / n

        if var_r > 0 and var_w > 0:
            corr = cov / (var_r ** 0.5 * var_w ** 0.5)
            print(f"  Pearson correlation: {corr:+.3f}")
            if corr > 0.3:
                print("  → POSITIVE: wider range = better win rate ✅")
            elif corr < -0.3:
                print("  → NEGATIVE: wider range = worse win rate ❌")
            else:
                print("  → NO correlation")


if __name__ == "__main__":
    main()
