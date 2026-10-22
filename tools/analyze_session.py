"""
Usage: python tools/analyze_session.py [path/to/<session_id>.json]
بدون آرگومان، جدیدترین session زیر data/paper_sessions را می‌خواند.
"""
import json, sys
from pathlib import Path

def analyze(path: Path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    s   = data["summary"]
    cyc = data["cycles"]

    sum_realized = sum((c.get("realized_pnl") or 0.0) for c in cyc)
    realized_events = [c for c in cyc if (c.get("realized_pnl") or 0.0) != 0.0]
    wins   = [c for c in realized_events if c["realized_pnl"] > 0]
    losses = [c for c in realized_events if c["realized_pnl"] < 0]

    delta = s["total_pnl"] - sum_realized

    print("=" * 62)
    print(f"SESSION {data['session_id']}")
    print(f"File:    {path}")
    print("=" * 62)
    print(f"Cycles:               {s['cycles_processed']}")
    print(f"  open_count:         {s['open_count']}")
    print(f"  close_count:        {s['close_count']}")
    print(f"  hold_count:         {s['hold_count']}")
    print(f"  error_cycles:       {s['error_cycles']}")
    print()
    print(f"Balance:              {s['balance']:.10f}")
    print(f"total_pnl (summary):  {s['total_pnl']:.10f}")
    print(f"sum(cycles):          {sum_realized:.10f}")
    print(f"DELTA:                {delta:+.10f}   <-- هر چیزی جز 0 یعنی باگ")
    print(f"Reconciled:           {abs(delta) < 1e-6}")
    print()
    print(f"trade_count (summary):{s['trade_count']}")
    print(f"realized events:      {len(realized_events)}")
    print(f"  wins:               {len(wins)}")
    print(f"  losses:             {len(losses)}")
    print()
    print("realized events detail:")
    for c in realized_events:
        pnl = c["realized_pnl"]
        print(f"  cycle {c['cycle']:>3} | {c.get('position_side') or '?':4} "
              f"@ {c.get('entry_price')} | "
              f"PnL {'+' if pnl>0 else ''}{pnl:.6f} | "
              f"err={c.get('error')}")

    fp = data.get("final_position")
    print()
    print(f"final_position open:  {bool(fp)}")
    if fp:
        print(f"  side={fp.get('side')} entry={fp.get('entry_price')} "
              f"qty={fp.get('quantity')} sl={fp.get('sl')} tp={fp.get('tp')} "
              f"partial_closed={fp.get('partial_closed')} "
              f"realized_partial_pnl={fp.get('realized_partial_pnl')}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        target = sorted(Path("data/paper_sessions").glob("*.json"),
                        key=lambda p: p.stat().st_mtime)[-1]
    analyze(target)
