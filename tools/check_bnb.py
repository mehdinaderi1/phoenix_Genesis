import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.futures_wrapper_v2 import XTFuturesExchange

w = XTFuturesExchange(dry_run=True)

with open("data/futures_runner_state_dry.json") as f:
    s = json.load(f)

print("=" * 60)
print("OPEN POSITIONS STATUS")
print("=" * 60)

for sym, info in s.get("active_positions", {}).items():
    price = w._get_price(sym)
    entry = info["entry"]
    initial = info.get("initial_entry", entry)
    side = info["side"]
    size = info["size"]
    csize = w.get_contract_size(sym) or 1
    tp = info.get("tp")
    hard_sl_pct = 5.0
    
    if side == "SHORT":
        pnl_pct = (entry - price) / entry * 100
        pnl_usd = (entry - price) * size * csize
        hard_sl = initial * (1 + hard_sl_pct / 100)
        dist_to_tp = (price - tp) / price * 100 if tp else None
        dist_to_sl = (hard_sl - price) / price * 100
    else:
        pnl_pct = (price - entry) / entry * 100
        pnl_usd = (price - entry) * size * csize
        hard_sl = initial * (1 - hard_sl_pct / 100)
        dist_to_tp = (tp - price) / price * 100 if tp else None
        dist_to_sl = (price - hard_sl) / price * 100
    
    print(f"\n{sym}: {side} {size} contracts")
    print(f"  Initial entry: {initial:.6g}")
    print(f"  Current entry: {entry:.6g}")
    print(f"  Current price: {price:.6g}")
    print(f"  PnL:           {pnl_pct:+.2f}%  (${pnl_usd:+.4f})")
    print(f"  TP:            {tp:.6g}  ({dist_to_tp:+.2f}% away)")
    print(f"  HardSL (5%):   {hard_sl:.6g}  ({dist_to_sl:+.2f}% away)")
    print(f"  Avg level:     {info.get('avg_count', 0)}/2")
    print(f"  Partial taken: {info.get('partial_taken', False)}")

print(f"\nClosed today: {len(s.get('closed_positions', []))}")
for c in s.get("closed_positions", [])[-3:]:
    print(f"  {c.get('symbol')}: {c.get('side')} reason={c.get('reason')} PnL=${c.get('pnl_usdt', 0):+.4f}")
