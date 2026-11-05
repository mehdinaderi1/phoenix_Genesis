import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exchanges.xt_exchange import XTExchange

spot = XTExchange(timeout=15)
pos = {
    "ARBUSDT": 0.16425,
    "OPUSDT": 0.105088,
    "PEPEUSDT": 5.112e-06,
    "AAVEUSDT": 131.241,
    "INJUSDT": 7.4637,
}
print(f"{'SYMBOL':12s} {'PRICE':>12s} {'AVG':>12s} {'PnL%':>8s} {'TP1?':>6s} {'TP2?':>6s}")
for sym, avg in pos.items():
    try:
        candles = spot.get_historical_candles(sym, "4H", limit=2)
        if candles:
            price = candles[-1]["close"]
            pnl = (price - avg) / avg * 100
            tp1 = "YES" if pnl >= 20 else "no"
            tp2 = "YES" if pnl >= 40 else "no"
            print(f"{sym:12s} {price:>12.6g} {avg:>12.6g} {pnl:>+7.2f}% {tp1:>6s} {tp2:>6s}")
    except Exception as e:
        print(f"{sym:12s} ERROR: {type(e).__name__}")
