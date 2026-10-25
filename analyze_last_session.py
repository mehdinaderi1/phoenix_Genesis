import json
import sys
from pathlib import Path

sessions = sorted(
    Path("data/paper_sessions").glob("*.json"),
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)
if not sessions:
    sys.exit("No sessions found")

s = sessions[0]
print(f"Analyzing: {s.name}")
print(f"Size: {s.stat().st_size / 1024:.1f} KB")

d = json.loads(s.read_text(encoding="utf-8"))
summary = d.get("summary", {})
print(f"\nCycles: {summary.get('cycles_processed')}")
print(f"Balance: {summary.get('balance'):.4f}")
print(f"Total PnL: {summary.get('total_pnl', 0):+.4f}")
print(f"Trades: {summary.get('trade_count')}")
print(f"Open: {summary.get('open_count')}")
print(f"Close: {summary.get('close_count')}")
print(f"Errors: {summary.get('error_cycles')}")
print(f"Blind: {summary.get('blind_cycles')}")

tp = sl = timeout = partial = 0
for c in d.get("cycles", []):
    r = (c.get("close_reason") or "").upper()
    if r == "SL": sl += 1
    elif r == "TP": tp += 1
    elif r == "TIMEOUT": timeout += 1
    if c.get("action") == "PARTIAL": partial += 1

print(f"\nBre akdown:")
print(f"  TP:      {tp}")
print(f"  SL:      {sl}")
print(f"  TIMEOUT: {timeout}")
print(f"  PARTIAL: {partial}")