import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exchanges.xt_exchange import XTExchange
from tools.futures_strategy_runner import compute_channel, candle_sig_with_volume

ex = XTExchange(timeout=10)
print("=" * 85)
print(f"{'SYMBOL':10s} {'pos%':>6s} {'wick_dn':>8s} {'wick_up':>8s} {'vol':>6s} {'setup':>6s}")
print("=" * 85)

for spot in ["APTUSDT", "JUPUSDT", "TIAUSDT", "VETUSDT", "HBARUSDT", "ICPUSDT", "NEARUSDT"]:
    cs = ex.get_historical_candles(spot, "4H", limit=40)
    if not cs or len(cs) < 20: continue
    ch = compute_channel(cs, 30)
    if not ch: continue
    price = cs[-1]["close"]
    pos = (price - ch["lower"]) / (ch["upper"] - ch["lower"]) * 100
    sig = candle_sig_with_volume(cs, window=10)
    if not sig: continue
    
    is_long = pos <= 25 and sig["lower_wick_pct"] >= 30 and sig["volume_confirmed"]
    is_short = pos >= 75 and sig["upper_wick_pct"] >= 30 and sig["volume_confirmed"]
    setup = "LONG" if is_long else ("SHORT" if is_short else "-")
    
    print(f"{spot:10s} {pos:5.1f}% {sig['lower_wick_pct']:7.1f}% "
          f"{sig['upper_wick_pct']:7.1f}% {sig['volume_ratio']:5.2f}x {setup:>6s}")
