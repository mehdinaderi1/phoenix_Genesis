import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.futures_wrapper_v2 import XTFuturesExchange

w = XTFuturesExchange(dry_run=False)

print("=" * 60)
print("ALL OPEN POSITIONS")
print("=" * 60)

positions = w.get_user_positions()

if not positions:
    print("(no positions - all clean)")
else:
    for p in positions:
        sym = p.get("symbol", "?")
        side = p.get("positionSide", "?")
        size = p.get("positionSize", "0")
        entry = p.get("entryPrice", "?")
        mark = p.get("markPrice") or p.get("lastPrice") or "?"
        pnl = p.get("unrealizedPnl") or p.get("profit") or "?"
        
        tag = ""
        if sym == "btc_usdt":
            tag = "[PROTECTED]"
        elif sym == "eth_usdt":
            tag = "[PROTECTED]"
        
        print(f"  {sym:12s} {side:5s} size={size:>8} entry={entry} {tag}")
        print(f"    mark={mark} PnL={pnl}")

print()
print("=" * 60)
bal = w.get_balance()
if bal:
    print(f"Balance: available=${bal['available']:.2f} equity=${bal['equity']:.2f}")
    print(f"         margin_used=${bal['margin_used']:.2f}")
