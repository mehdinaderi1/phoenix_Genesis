# analyze_5x.py — تحلیل 5x Maker
import json
from pathlib import Path
from collections import Counter

# فقط session های جدید (5x)
sessions = sorted(Path("data/paper_sessions").glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

total_pnl = 0.0
total_trades = 0
sl_count = 0
tp_count = 0
partial_count = 0
timeout_count = 0

for s in sessions[:10]:  # فقط ۱۰ session آخر
    d = json.loads(s.read_text(encoding="utf-8"))
    summary = d.get("summary", {})
    pnl = summary.get("total_pnl", 0.0)
    trade_count = summary.get("trade_count", 0)
    
    if trade_count == 0:
        continue
    
    total_pnl += pnl
    total_trades += trade_count
    
    # شمارش reason از cycles
    for c in d.get("cycles", []):
        reason = c.get("close_reason")
        if reason == "SL":
            sl_count += 1
        elif reason == "TP":
            tp_count += 1
        elif reason == "TIMEOUT":
            timeout_count += 1
        if c.get("action") == "PARTIAL":
            partial_count += 1
    
    print(f"{s.name[:20]}: {trade_count} trades | PnL {pnl:+.4f} | {reason if 'reason' in dir() else ''}")

print()
print("=" * 50)
print(f"Total trades: {total_trades}")
print(f"SL:     {sl_count}")
print(f"TP:     {tp_count}")
print(f"TIMEOUT:{timeout_count}")
print(f"PARTIAL: {partial_count}")
if total_trades > 0:
    wr = tp_count / total_trades * 100
    print(f"Win rate: {wr:.1f}%")
print(f"Total PnL: {total_pnl:+.4f} USDT")
