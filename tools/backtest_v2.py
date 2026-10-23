"""
Backtest v2 — fixes for short-session bias:
- Report entries even when resolved trades = 0
- Filter to long sessions (>= 50 cycles)
- Mark-to-market unresolved positions at session end
- Report cycle-length distribution
"""
import json
from pathlib import Path

ROOT = Path("data/paper_sessions")
ORPHANED = ROOT / "_orphaned"
FEE_PCT = 0.0012


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
    entries = 0
    in_pos = False
    entry = None
    direction = None
    entry_cycle = None
    last_price = None

    for i, c in enumerate(cycles):
        price = c.get("price")
        if price is None or price <= 0:
            continue
        last_price = price

        if in_pos:
            if direction == "BUY":
                if price <= entry * (1 - sl_pct):
                    trades.append({"result": "SL", "pnl_pct": -sl_pct - FEE_PCT, "duration": i - entry_cycle})
                    in_pos = False
                elif price >= entry * (1 + tp_pct):
                    trades.append({"result": "TP", "pnl_pct": tp_pct - FEE_PCT, "duration": i - entry_cycle})
                    in_pos = False
            else:
                if price >= entry * (1 + sl_pct):
                    trades.append({"result": "SL", "pnl_pct": -sl_pct - FEE_PCT, "duration": i - entry_cycle})
                    in_pos = False
                elif price <= entry * (1 - tp_pct):
                    trades.append({"result": "TP", "pnl_pct": tp_pct - FEE_PCT, "duration": i - entry_cycle})
                    in_pos = False
            continue

        signal = (c.get("signal") or "").upper()
        confidence = c.get("confidence") or 0
        if signal in ("BUY", "SELL") and confidence >= min_conf:
            entry = price
            direction = signal
            entry_cycle = i
            in_pos = True
            entries += 1

    # Mark-to-market unresolved at session end
    unresolved = 0
    if in_pos and last_price is not None:
        if direction == "BUY":
            pnl = (last_price - entry) / entry - FEE_PCT
        else:
            pnl = (entry - last_price) / entry - FEE_PCT
        trades.append({"result": "OPEN", "pnl_pct": pnl, "duration": len(cycles) - entry_cycle})
        unresolved = 1

    return trades, entries, unresolved


def run_config(all_sessions, min_conf, sl, tp):
    all_trades = []
    total_entries = 0
    total_unresolved = 0
    sessions_with_trades = 0

    for sid, data in all_sessions:
        trades, entries, unresolved = backtest_one(data.get("cycles", []), min_conf, sl, tp)
        if trades:
            sessions_with_trades += 1
        all_trades.extend(trades)
        total_entries += entries
        total_unresolved += unresolved

    wins = sum(1 for t in all_trades if t["result"] == "TP")
    losses = sum(1 for t in all_trades if t["result"] == "SL")
    opens = sum(1 for t in all_trades if t["result"] == "OPEN")
    n = len(all_trades)
    total_pnl = sum(t["pnl_pct"] for t in all_trades)
    ev = (total_pnl / n * 100) if n > 0 else 0.0
    winrate = (wins / n * 100) if n > 0 else 0.0

    return {
        "entries": total_entries, "trades": n,
        "wins": wins, "losses": losses, "opens": opens,
        "sessions": sessions_with_trades,
        "winrate": winrate, "ev": ev,
        "total_pnl": total_pnl * 100,
    }


def main():
    # ─── Distribution of session lengths ───
    all_sess = list(iter_sessions())
    buckets = {"1-20": 0, "20-50": 0, "50-100": 0, "100+": 0}
    for _, d in all_sess:
        n = len(d.get("cycles", []))
        b = "1-20" if n < 20 else "20-50" if n < 50 else "50-100" if n < 100 else "100+"
        buckets[b] += 1

    print("=" * 105)
    print("Session length distribution")
    print("=" * 105)
    for k, v in buckets.items():
        print(f"  {k:>8} cycles: {v:>4} sessions")
    long_sess = [(sid, d) for sid, d in all_sess if len(d.get("cycles", [])) >= 50]
    total_long_cycles = sum(len(d.get("cycles", [])) for _, d in long_sess)
    print(f"  Long sessions (>=50 cyc): {len(long_sess)} ({total_long_cycles} cycles)")
    print()

    # ─── Phase 1: confidence sweep on long sessions ───
    print("=" * 125)
    print(f"Phase 1: Confidence sweep on {len(long_sess)} long sessions (SL=0.5%, TP=1.0%, MTM unresolved)")
    print("=" * 125)
    header = f"{'conf':>5} {'entries':>8} {'resolved':>9} {'TP':>4} {'SL':>4} {'OPEN':>5} {'winrate':>8} {'EV%':>9} {'total%':>9} {'sess':>5}"
    print(header)
    print("-" * 125)

    for conf in (30, 40, 50, 60, 70, 80):
        r = run_config(long_sess, conf, 0.005, 0.010)
        print(f"{conf:>5} {r['entries']:>8} {r['wins']+r['losses']:>9} "
              f"{r['wins']:>4} {r['losses']:>4} {r['opens']:>5} "
              f"{r['winrate']:>7.1f}% {r['ev']:>+8.4f}% "
              f"{r['total_pnl']:>+8.2f}% {r['sessions']:>5}")

    # ─── Phase 2: SL/TP sweep at conf=50 on long sessions ───
    print()
    print("=" * 125)
    print("Phase 2: SL/TP sweep at conf=50 on long sessions")
    print("=" * 125)
    print(f"{'sl%':>5} {'tp%':>5} {'entries':>8} {'TP':>4} {'SL':>4} {'OPEN':>5} {'winrate':>8} {'EV%':>9} {'total%':>9} {'RR':>5} {'sess':>5}")
    print("-" * 125)

    configs = [
        (0.003, 0.006), (0.003, 0.009), (0.003, 0.012),
        (0.005, 0.010), (0.005, 0.015), (0.005, 0.020),
        (0.010, 0.020), (0.010, 0.030),
    ]
    for sl, tp in configs:
        r = run_config(long_sess, 50, sl, tp)
        if r["entries"] == 0:
            continue
        print(f"{sl*100:>5.1f} {tp*100:>5.1f} {r['entries']:>8} "
              f"{r['wins']:>4} {r['losses']:>4} {r['opens']:>5} "
              f"{r['winrate']:>7.1f}% {r['ev']:>+8.4f}% "
              f"{r['total_pnl']:>+8.2f}% {tp/sl:>5.1f} {r['sessions']:>5}")

    # ─── Phase 3: Best config ───
    print()
    print("=" * 105)
    print("Phase 3: Best config by EV (min 10 resolved)")
    print("=" * 105)
    best = []
    for conf in (30, 40, 50, 60, 70, 80):
        for sl, tp in configs:
            r = run_config(long_sess, conf, sl, tp)
            if r["wins"] + r["losses"] >= 10:
                best.append((conf, sl, tp, r))
    best.sort(key=lambda x: x[3]["ev"], reverse=True)
    for conf, sl, tp, r in best[:5]:
        print(f"  conf={conf}  SL={sl*100:.1f}%  TP={tp*100:.1f}%  "
              f"entries={r['entries']}  TP={r['wins']}  SL={r['losses']}  "
              f"winrate={r['winrate']:.1f}%  EV={r['ev']:+.4f}%")
    if not best:
        print("  (no config produced >= 10 resolved trades)")


if __name__ == "__main__":
    main()