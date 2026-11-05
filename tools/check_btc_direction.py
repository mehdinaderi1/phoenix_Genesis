import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exchanges.xt_exchange import XTExchange
from tools.futures_strategy_runner import btc_direction, _close, ema

spot = XTExchange(timeout=15)
c4h = spot.get_historical_candles("BTCUSDT", "4H", limit=100)
print(f"Total 4H candles: {len(c4h)}")

# حالت فعلی (بدون کندل جاری)
closed = c4h[:-1]
print(f"Closed candles used: {len(closed)}")
closes_closed = [_close(c) for c in closed]
e20 = ema(closes_closed, 20)
e50 = ema(closes_closed, 50)
diff = (e20 - e50) / e50 * 100
print(f"\n[بدون کندل جاری]")
print(f"  EMA20 = {e20:.2f}")
print(f"  EMA50 = {e50:.2f}")
print(f"  diff  = {diff:+.3f}%  →  {btc_direction(closed)}")

# حالت با کندل جاری (فرضی)
closes_all = [_close(c) for c in c4h]
e20b = ema(closes_all, 20)
e50b = ema(closes_all, 50)
diffb = (e20b - e50b) / e50b * 100
print(f"\n[با کندل جاری]")
print(f"  EMA20 = {e20b:.2f}")
print(f"  EMA50 = {e50b:.2f}")
print(f"  diff  = {diffb:+.3f}%")

# آخرین کندل ۴H جاری چقدر نزولی است؟
cur = c4h[-1]
o, c = _close(c4h[-2]), _close(c4h[-1])
print(f"\n[کندل ۴H جاری]")
print(f"  open={cur['open']:.2f} high={cur['high']:.2f} low={cur['low']:.2f} close={cur['close']:.2f}")
print(f"  تغییر در کندل: {(c - cur['open'])/cur['open']*100:+.2f}%")

# برای DOWN چقدر لازم است؟
print(f"\n[فاصله تا DOWN]")
print(f"  آستانه: -0.5%")
print(f"  فعلی: {diff:+.3f}%")
print(f"  فاصله: {abs(diff - (-0.5)):.3f}%")
