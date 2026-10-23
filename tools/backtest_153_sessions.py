"""
Backtest 153 sessions × confidence threshold × SL/TP grid.

Uses ONLY signal + confidence + price from session cycles.
Ignores the actual action taken by the runtime.

Answers: does confidence filtering + SL/TP tuning give positive EV?
"""
import json
from pathlib import Path

ROOT = Path("data/paper_sessions")
ORPHANED = ROOT / "_orphaned"

FEE_PCT = 0.0012   # 0.12% round trip (0.06% × 2)


def iter_sessions():
    for d in (ROOT, ORPHANED):
        if not d.exists():
            continue
        for path in sorted(d.glob("*.json")):
            if path.name.endswith(".checkpoint.json"):
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            yield path.stem, data


def backtest_one(cycles, min_conf, sl_pct, tp_pct):
    trades = []
    unresolved = 0
    in_pos = False
    entry = None
    direction = None
    entry_cycle = None

    for i, c in enumerate(cycles):
        price = c.get("price")
        if price is None or price <= 0:
            continue

        if in_pos:
            if direction == "BUY":
                if price <= entry * (1 - sl_pct):
                    trades.append({"result": "SL", "pnl_pct": -sl_pct - FEE_PCT,
                                   "duration": i - entry_cycle})
                    in_pos = False
                elif price >= entry * (1 + tp_pct):
                    trades.append({"result": "TP", "pnl_pct": tp_pct - FEE_PCT,
                                   "duration": i - entry_cycle})
                    in_pos = False
            else:
                if price >= entry * (1 + sl_pct):
                    trades.append({"result": "SL", "pnl_pct": -sl_pct - FEE_PCT,
                                   "duration": i - entry_cycle})
                    in_pos = False
                elif price <= entry * (1 - tp_pct):
                    trades.append({"result": "TP", "pnl_pct": tp_pct - FEE_PCT,
                                   "duration": i - entry_cycle})
                    in_pos = False
            continue

        signal = (c.get("signal") or "").upper()
        confidence = c.get("confidence") or 0
        if signal in ("BUY", "SELL") and confidence >= min_conf:
            entry = price
            direction = signal
            entry_cycle = i
            in_pos = True

    if in_pos:
        unresolved = 1

    return trades, unresolved


def run_config(all_sessions, min_conf, sl, tp):
    all_trades = []
    total_unresolved = 0
    sessions_with_trades = 0

    for sid, data in all_sessions:
        trades, unresolved = backtest_one(
            data.get("cycles", []), min_conf, sl, tp
        )
        if trades:
            sessions_with_trades += 1
        all_trades.extend(trades)
        total_unresolved += unresolved

    wins = sum(1 for t in all_trades if t["result"] == "TP")
    losses = sum(1 for t in all_trades if t["result"] == "SL")
    n = len(all_trades)
    total_pnl = sum(t["pnl_pct"] for t in all_trades)
    ev = (total_pnl / n * 100) if n > 0 else 0.0
    winrate = (wins / n * 100) if n > 0 else 0.0
    avg_dur = (sum(t["duration"] for t in all_trades) / n) if n > 0 else 0.0

    return {
        "trades": n, "wins": wins, "losses": losses,
        "unresolved": total_unresolved,
        "sessions": sessions_with_trades,
        "winrate": winrate, "ev": ev,
        "total_pnl": total_pnl * 100,
        "avg_dur": avg_dur,
    }


def main():
    sessions = list(iter_sessions())
    total_cycles = sum(len(d.get("cycles", [])) for _, d in sessions)
    print(f"Loaded {len(sessions)} sessions ({total_cycles} cycles)")
    print()

    print("=" * 105)
    print("Phase 1: Confidence threshold sweep (SL=1.0%, TP=2.0%)")
    print("=" * 105)
    print(f"{'conf':>5} {'trades':>7} {'wins':>5} {'loss':>5} {'unres':>6} "
          f"{'winrate':>8} {'EV%':>9} {'total%':>9} {'avgDur':>7} {'sess':>5}")
    print("-" * 105)

    for conf in (40, 50, 60, 70, 80):
        r = run_config(sessions, conf, 0.01, 0.02)
        if r["trades"] == 0:
            print(f"{conf:>5} {r['trades']:>7}  (no trades)")
            continue
        print(f"{conf:>5} {r['trades']:>7} {r['wins']:>5} {r['losses']:>5} "
              f"{r['unresolved']:>6} {r['winrate']:>7.1f}% "
              f"{r['ev']:>+8.4f}% {r['total_pnl']:>+8.2f}% "
              f"{r['avg_dur']:>6.1f} {r['sessions']:>5}")

    print()
    print("=" * 105)
    print("Phase 2: SL/TP sweep at confidence=70")
    print("=" * 105)
    print(f"{'sl%':>5} {'tp%':>5} {'trades':>7} {'wins':>5} {'loss':>5} {'unres':>6} "
          f"{'winrate':>8} {'EV%':>9} {'total%':>9} {'RR':>5} {'sess':>5}")
    print("-" * 105)

    configs = [
        (0.005, 0.010), (0.005, 0.015),
        (0.010, 0.015), (0.010, 0.020), (0.010, 0.025), (0.010, 0.030),
        (0.015, 0.020), (0.015, 0.030),
        (0.020, 0.020), (0.020, 0.030), (0.020, 0.040),
    ]

    for sl, tp in configs:
        r = run_config(sessions, 70, sl, tp)
        if r["trades"] == 0:
            continue
        rr = tp / sl
        print(f"{sl*100:>5.1f} {tp*100:>5.1f} {r['trades']:>7} {r['wins']:>5} "
              f"{r['losses']:>5} {r['unresolved']:>6} "
              f"{r['winrate']:>7.1f}% {r['ev']:>+8.4f}% "
              f"{r['total_pnl']:>+8.2f}% {rr:>5.1f} {r['sessions']:>5}")

    print()
    print("=" * 105)
    print("Phase 3: Best 3 configs by EV (min 10 trades)")
    print("=" * 105)

    best = []
    for conf in (40, 50, 60, 70, 80):
        for sl, tp in configs:
            r = run_config(sessions, conf, sl, tp)
            if r["trades"] >= 10:
                best.append((conf, sl, tp, r))

    best.sort(key=lambda x: x[3]["ev"], reverse=True)
    for conf, sl, tp, r in best[:3]:
        print(f"  conf={conf}  SL={sl*100:.1f}%  TP={tp*100:.1f}%  "
              f"trades={r['trades']}  winrate={r['winrate']:.1f}%  "
              f"EV={r['ev']:+.4f}%")

    print()
    print("Notes:")
    print(f"  - Fee: {FEE_PCT*100:.2f}% round trip")
    print("  - Unresolved = position still open at session end (excluded from EV)")


if __name__ == "__main__":
    main()