import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.futures_wrapper_v2 import XTFuturesExchange

w = XTFuturesExchange(dry_run=False)

print("=" * 60)
print("CURRENT FET STATE")
print("=" * 60)

for p in w.get_user_positions():
    sym = p.get("symbol", "?")
    if sym == "fet_usdt":
        print(f"  FET: {p.get('positionSide')} size={p.get('positionSize')} "
              f"entry={p.get('entryPrice')}")
        print(f"  mark={p.get('markPrice') or p.get('lastPrice')}")
        print(f"  PnL={p.get('unrealizedPnl') or p.get('profit')}")
    else:
        print(f"  {sym}: {p.get('positionSide')} size={p.get('positionSize')}")

print()
bal = w.get_balance()
if bal:
    print(f"Balance: available=${bal['available']:.2f} "
          f"equity=${bal['equity']:.2f} margin_used=${bal['margin_used']:.2f}")
