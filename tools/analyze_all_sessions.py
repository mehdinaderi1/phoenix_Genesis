"""
Usage: python tools/analyze_all_sessions.py [--orphaned-only] [--csv out.csv]
اسکن همهٔ *.json در data/paper_sessions/ + _orphaned/
"""
import json, sys, csv
from pathlib import Path

def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"_error": str(e)}

def analyze_one(path):
    d = load(path)
    if "_error" in d:
        return {"session": path.stem, "load_error": d["_error"]}
    s = d.get("summary") or {}
    cyc = d.get("cycles") or []
    sum_realized = sum((c.get("realized_pnl") or 0.0) for c in cyc)
    total = s.get("total_pnl", 0.0)
    delta = total - sum_realized
    realized_events = [c for c in cyc if (c.get("realized_pnl") or 0.0) != 0.0]
    return {
        "session": d.get("session_id", path.stem),
        "where": "_orphaned" if path.parent.name == "_orphaned" else "root",
        "cycles": s.get("cycles_processed", 0),
        "trades": s.get("trade_count", 0),
        "realized_events": len(realized_events),
        "total_pnl": total,
        "sum_cycles_pnl": sum_realized,
        "delta": delta,
        "reconciled": abs(delta) < 1e-6,
        "error_cycles": s.get("error_cycles", 0),
        "final_open": bool(d.get("final_position")),
        "file_size": path.stat().st_size,
    }

def main():
    args = sys.argv[1:]
    only_orph = "--orphaned-only" in args
    csv_out = None
    if "--csv" in args:
        csv_out = Path(args[args.index("--csv") + 1])

    root = Path("data/paper_sessions")
    paths = list(root.glob("*.json"))
    if not only_orph:
        paths += list((root / "_orphaned").glob("*.json"))
    else:
        paths = list((root / "_orphaned").glob("*.json"))
    paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    rows = [analyze_one(p) for p in paths]

    print(f"{'session':36} {'where':10} {'cyc':>5} {'trd':>4} {'evt':>4} "
          f"{'total_pnl':>13} {'delta':>13} {'ok':>3} {'err':>4} {'open':>4}")
    print("-" * 120)
    bad = 0
    for r in rows:
        if "load_error" in r:
            print(f"{r['session']:36} LOAD_ERROR: {r['load_error']}")
            continue
        ok = "Y" if r["reconciled"] else "N"
        if not r["reconciled"]:
            bad += 1
        print(f"{r['session']:36} {r['where']:10} {r['cycles']:>5} "
              f"{r['trades']:>4} {r['realized_events']:>4} "
              f"{r['total_pnl']:>13.6f} {r['delta']:>13.6f} "
              f"{ok:>3} {r['error_cycles']:>4} "
              f"{'Y' if r['final_open'] else 'n':>4}")
    print("-" * 120)
    total = sum(r.get("total_pnl", 0.0) for r in rows if "load_error" not in r)
    n_bad = sum(1 for r in rows if "load_error" not in r and not r["reconciled"])
    print(f"Total sessions: {len(rows)}  |  "
          f"Unreconciled: {n_bad}/{len(rows)-sum(1 for r in rows if 'load_error' in r)}  |  "
          f"Sum total_pnl: {total:.6f}")
    print(f"{'-- all clean!' if n_bad == 0 else '-- ' + str(n_bad) + ' sessions need attention'}")

    if csv_out:
        with open(csv_out, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            for r in rows:
                if "load_error" not in r:
                    w.writerow(r)
        print(f"CSV written: {csv_out}")

if __name__ == "__main__":
    main()
