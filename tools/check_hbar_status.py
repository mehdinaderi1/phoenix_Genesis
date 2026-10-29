import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.futures_wrapper_v2 import XTFuturesExchange

w = XTFuturesExchange(dry_run=True)

with open("data/futures_runner_state_dry.json") as f:
    s = json.load(f)

print("=" * 60)
print("STATE FILE STATUS")
print("=" * 60)

active = s.get("active_positions", {})
closed = s.get("closed_positions", [])

print(f"Active positions: {len(active)}")
for sym, info in active.items():
    price = w._get_price(sym)
    entry = info["entry"]
    side = info["side"]
    if price and entry:
        if side == "LONG":
            pnl_pct = (price - entry) / entry * 100
        else:
            pnl_pct = (entry - price) / entry * 100
        print(f"  {sym}: {side} entry={entry} price={price} PnL={pnl_pct:+.2f}%")
        print(f"    SL={info['sl']} TP={info['tp']}")
        print(f"    Opened at: {info.get('opened_at', '?')}")
    else:
        print(f"  {sym}: {side} entry={entry} price=UNAVAILABLE")

print(f"\nClosed positions: {len(closed)}")
for c in closed:
    print(f"  {c.get('symbol')}: {c.get('side')} entry={c.get('entry')} "
          f"closed_at={c.get('closed_at')}")

print(f"\nSession started: {s.get('started_at', '?')}")
print(f"Last cycle: {s.get('last_cycle', '?')}")
print(f"Daily start equity: ${s.get('daily_start_equity', '?')}")
