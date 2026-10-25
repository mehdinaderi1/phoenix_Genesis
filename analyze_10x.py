# analyze_10x.py — آمار کامل 10x Maker (شامل پوزیشن‌های باز)
import json
from pathlib import Path

sessions = sorted(
    Path("data/paper_sessions").glob("*.json"),
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)[:5]

total_pnl = 0.0
total_trades = 0
open_positions = 0
sl_count = tp_count = timeout_count = partial_count = 0

for s in sessions:
    try:
        d = json.loads(s.read_text(encoding="utf-8"))
    except Exception:
        continue
    summary = d.get("summary", {})
    total_pnl += summary.get("total_pnl", 0.0) or 0.0
    tc = summary.get("trade_count", 0) or 0
    total_trades += tc
    fp = d.get("final_position")
    if fp and fp.get("side"):
        open_positions += 1
    for c in d.get("cycles", []):
        r = (c.get("close_reason") or "").upper()
        pnl_c = c.get("realized_pnl") or 0.0
        if r == "SL": 
            sl_count += 1
        elif r == "TP":
            tp_count += 1
        elif r == "TIMEOUT":
            timeout_count += 1
        elif r in ("", None) and c.get("action") == "CLOSE" and pnl_c > 0:
            # fallback: close با سود اما بدون برچسب → TP
            tp_count += 1
        elif r in ("", None) and c.get("action") == "CLOSE" and pnl_c < 0:
            sl_count += 1
        if c.get("action") == "PARTIAL":
            partial_count += 1

print("=" * 55)
print("10x MAKER - METRICS")
print("=" * 55)
print(f"Closed trades:    {total_trades}")
print(f"Open positions:   {open_positions}")
print(f"  TP:             {tp_count}")
print(f"  SL:             {sl_count}")
print(f"  TIMEOUT:        {timeout_count}")
print(f"  PARTIAL:        {partial_count}")
if total_trades > 0:
    wr = (tp_count / total_trades) * 100
    print(f"Win rate:         {wr:.1f}%")
print(f"Realized PnL:     {total_pnl:+.4f} USDT")