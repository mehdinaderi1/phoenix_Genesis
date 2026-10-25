#!/usr/bin/env python3
"""
Regime Performance Analysis
Correlates market regime with trading outcomes.

Usage:
    python tools/regime_analysis.py data/paper_sessions/*.json
"""
import json
import sys
from pathlib import Path
from collections import defaultdict


def analyze_sessions(files):
    by_regime = defaultdict(lambda: {
        "open_count": 0,
        "close_count": 0,
        "wins": 0,
        "losses": 0,
        "total_pnl": 0.0,
        "partial_count": 0,
        "sl_move_count": 0,
        "cycles_seen": 0,
    })

    for path in files:
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception as e:
            print(f"SKIP {path}: {e}")
            continue

        for cycle in data.get("cycles", []):
            regime = cycle.get("regime") or "UNKNOWN"
            action = cycle.get("action") or "HOLD"
            pnl = cycle.get("realized_pnl", 0) or 0

            stats = by_regime[regime]
            stats["cycles_seen"] += 1

            if action == "OPEN":
                stats["open_count"] += 1
            elif action in ("CLOSE", "RECOVERY_CLOSE"):
                stats["close_count"] += 1
                if pnl > 0:
                    stats["wins"] += 1
                elif pnl < 0:
                    stats["losses"] += 1
                stats["total_pnl"] += pnl
            elif action == "PARTIAL":
                stats["partial_count"] += 1
                stats["total_pnl"] += pnl
            elif action == "SL_MOVE":
                stats["sl_move_count"] += 1

    return by_regime


def print_report(by_regime):
    print()
    print("=" * 85)
    print("REGIME PERFORMANCE ANALYSIS")
    print("=" * 85)
    print()
    print(f"{'Regime':<22} {'Cycles':>7} {'Trades':>7} {'Wins':>5} {'Loss':>5} {'Win%':>7} {'PnL':>12}")
    print("-" * 85)

    total_wins = 0
    total_losses = 0
    total_pnl = 0.0

    for regime in sorted(by_regime.keys()):
        s = by_regime[regime]
        trades = s["wins"] + s["losses"]
        win_pct = (s["wins"] / trades * 100) if trades > 0 else 0.0

        print(f"{regime:<22} {s['cycles_seen']:>7} {trades:>7} {s['wins']:>5} "
              f"{s['losses']:>5} {win_pct:>6.1f}% {s['total_pnl']:>+12.4f}")

        total_wins += s["wins"]
        total_losses += s["losses"]
        total_pnl += s["total_pnl"]

    print("-" * 85)
    total_trades = total_wins + total_losses
    total_win_pct = (total_wins / total_trades * 100) if total_trades > 0 else 0.0
    print(f"{'TOTAL':<22} {sum(s['cycles_seen'] for s in by_regime.values()):>7} "
          f"{total_trades:>7} {total_wins:>5} {total_losses:>5} "
          f"{total_win_pct:>6.1f}% {total_pnl:>+12.4f}")

    print()
    print("=" * 85)
    print("RECOMMENDATIONS")
    print("=" * 85)

    for regime in sorted(by_regime.keys()):
        s = by_regime[regime]
        trades = s["wins"] + s["losses"]
        if trades < 3:
            print(f"  {regime:<22} ⏸  insufficient data ({trades} trades)")
            continue
        win_pct = s["wins"] / trades * 100

        if win_pct >= 55 and s["total_pnl"] > 0:
            print(f"  {regime:<22} ✅ PROFITABLE (win {win_pct:.0f}%, pnl {s['total_pnl']:+.4f})")
        elif win_pct >= 45:
            print(f"  {regime:<22} 🟡 BREAKEVEN (win {win_pct:.0f}%, pnl {s['total_pnl']:+.4f})")
        else:
            print(f"  {regime:<22} ❌ UNPROFITABLE (win {win_pct:.0f}%, pnl {s['total_pnl']:+.4f})")


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/regime_analysis.py data/paper_sessions/*.json")
        sys.exit(1)

    files = sys.argv[1:]
    print(f"Analyzing {len(files)} session file(s)...")

    by_regime = analyze_sessions(files)
    if not by_regime:
        print("No data found")
        return

    print_report(by_regime)


if __name__ == "__main__":
    main()
