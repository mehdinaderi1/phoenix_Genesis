# analyze_10x.py — آمار کامل 10x Maker
import json
from pathlib import Path

sessions = sorted(
    Path("data/paper_sessions").glob("*.json"),
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)[:5]

total_pnl = 0.0
total_trades = 0
sl_count = tp_count = timeout_count = partial_count = 0

for s in sessions:
    try:
        d = json.loads(s.read_text(encoding="utf-8"))
    except Exception:
        continue
    summary = d.get("summary", {})
    pnl = summary.get("total_pnl", 0.0)
    tc = summary.get("trade_count", 0)
    if tc == 0:
        continue
    total_pnl += pnl
    total_trades += tc
    for c in d.get("cycles", []):
        r = c.get("close_reason")
        if r == "SL": sl_count += 1
        elif r == "TP": tp_count += 1
        elif r == "TIMEOUT": timeout_count += 1
        if c.get("action") == "PARTIAL": partial_count += 1

print("=" * 55)
print("10x MAKER - METRICS")
print("=" * 55)
print(f"Total trades: {total_trades}")
print(f"  TP:       {tp_count}")
print(f"  SL:       {sl_count}")
print(f"  TIMEOUT:  {timeout_count}")
print(f"  PARTIAL:  {partial_count}")
if total_trades > 0:
    wr = (tp_count / total_trades) * 100
    print(f"Win rate: {wr:.1f}%")
print(f"Total PnL: {total_pnl:+.4f} USDT")
