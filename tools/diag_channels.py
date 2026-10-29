"""
tools/diag_channels.py — READ-ONLY channel diagnostic (no orders, no state change)
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exchanges.xt_exchange import XTExchange
from tools.futures_strategy_runner import (
    SYMBOLS, TIMEFRAME, CHANNEL_PERIOD, MIN_WIDTH_PCT, MAX_WIDTH_PCT,
    LONG_MAX_POS, SHORT_MIN_POS,
    compute_channel, btc_direction, candle_sig_with_volume, _close,
)

spot = XTExchange(timeout=15)

print("[Diag] BTC direction...")
try:
    btc_dir = btc_direction(spot.get_historical_candles("BTCUSDT", TIMEFRAME, limit=100))
except Exception as e:
    btc_dir = f"ERR({e})"
print(f"[Diag] BTC = {btc_dir}\n")

rows, failed = [], []
for sym in SYMBOLS:
    try:
        candles = spot.get_historical_candles(sym, TIMEFRAME, limit=CHANNEL_PERIOD + 20)
    except Exception as e:
        failed.append((sym, str(e)[:50])); continue
    if not candles or len(candles) < CHANNEL_PERIOD + 5:
        failed.append((sym, f"short data")); continue
    ch = compute_channel(candles, CHANNEL_PERIOD)
    if not ch:
        failed.append((sym, "no channel")); continue
    price = _close(candles[-1])
    rng = ch["upper"] - ch["lower"]
    pos = (price - ch["lower"]) / rng * 100 if rng > 0 else 0
    sig = candle_sig_with_volume(candles, window=10) or {}
    rows.append(dict(
        sym=sym, price=price, lower=ch["lower"], upper=ch["upper"],
        width=ch["width_pct"], pos=pos,
        lw=sig.get("lower_wick_pct", 0), uw=sig.get("upper_wick_pct", 0),
        vol=sig.get("volume_ratio", 0), vol_ok=sig.get("volume_confirmed", False),
    ))
    time.sleep(0.2)

rows.sort(key=lambda r: r["pos"])

print(f"{'SYMBOL':11s} {'PRICE':>11s} {'LOWER':>11s} {'UPPER':>11s} "
      f"{'WIDTH%':>7s} {'POS%':>7s} {'lowWk':>6s} {'vol':>5s}  FLAGS")
print("-" * 108)
for r in rows:
    flags = []
    if r["pos"] < 0:                        flags.append("BROKE_FLOOR")
    elif r["pos"] <= 5:                     flags.append("AT_FLOOR")
    if r["width"] < MIN_WIDTH_PCT:          flags.append("width<min")
    if r["width"] > MAX_WIDTH_PCT:          flags.append("width>max")
    if r["pos"] >= SHORT_MIN_POS and r["uw"] >= 30 and r["vol_ok"]:
        flags.append("SHORT_CANDIDATE")
    if r["pos"] <= LONG_MAX_POS and r["lw"] >= 30 and r["vol_ok"]:
        flags.append("LONG_CANDIDATE")
    print(f"{r['sym']:11s} {r['price']:>11.6g} {r['lower']:>11.6g} {r['upper']:>11.6g} "
          f"{r['width']:>7.2f} {r['pos']:>7.1f} {r['lw']:>6.1f} {r['vol']:>5.2f}  {','.join(flags) or '-'}")

print(f"\nSummary: ok={len(rows)} failed={len(failed)}")
for s, e in failed:
    print(f"  FAIL {s}: {e}")