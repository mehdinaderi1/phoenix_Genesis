# tools/test_ratio_filter.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exchanges.xt_exchange import XTExchange
from tools.futures_strategy_runner import _close, TIMEFRAME

spot = XTExchange(timeout=15)

# تست نسبت برای چند نماد
for sym in ["OPUSDT", "ETHUSDT", "AAVEUSDT"]:
    try:
        alt = spot.get_historical_candles(sym, TIMEFRAME, limit=15)
        btc = spot.get_historical_candles("BTCUSDT", TIMEFRAME, limit=15)
        if not alt or not btc:
            print(f"{sym}: NO DATA")
            continue
        ratios = []
        for i in range(min(len(alt), len(btc))):
            a = _close(alt[i])
            b = _close(btc[i])
            if b > 0:
                ratios.append(a / b)
        
        if len(ratios) >= 10:
            recent = ratios[-1]
            past = ratios[-10]
            trend = "UP" if recent > past else "DOWN"
            print(f"{sym}: ratio trend = {trend} (recent={recent:.6g}, past={past:.6g})")
        else:
            print(f"{sym}: not enough data")
    except Exception as e:
        print(f"{sym}: ERROR {type(e).__name__}")