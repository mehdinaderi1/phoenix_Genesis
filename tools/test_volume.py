import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exchanges.xt_exchange import XTExchange
from tools.futures_strategy_runner import candle_sig_with_volume, to_futures_symbol

ex = XTExchange(timeout=10)
print("=" * 70)
print(f"{'SYMBOL':12s} {'wick_up':>8s} {'wick_dn':>8s} {'vol':>6s} {'confirmed':>10s}")
print("=" * 70)
for spot in ["APTUSDT", "JUPUSDT", "TIAUSDT", "VETUSDT", "HBARUSDT"]:
    cs = ex.get_historical_candles(spot, "4H", limit=40)
    if not cs or len(cs) < 15:
        print(f"{spot:12s} (no data)")
        continue
    sig = candle_sig_with_volume(cs, window=10, min_ratio=1.2)
    if not sig:
        print(f"{spot:12s} (sig none)")
        continue
    print(f"{spot:12s} {sig['upper_wick_pct']:>7.1f}% {sig['lower_wick_pct']:>7.1f}% "
          f"{sig['volume_ratio']:>5.2f}x {str(sig['volume_confirmed']):>10s}")
