"""
Pullback Detector with BTC Filter for Phoenix Genesis.
Implements the complete strategy:
  1. BTC direction filter (never trade against BTC)
  2. Trend + Pullback logic
  3. Channel edge entry (4H Donchian)
  4. Two-way setups (LONG at bottom, SHORT at top)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
from datetime import datetime
from exchanges.xt_exchange import XTExchange


# ═══════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════

SYMBOLS = [
    "BTCUSDT",  # always first (used as filter)
    "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
    "ZECUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT",
    "DOTUSDT", "POLUSDT", "NEARUSDT", "APTUSDT",
    "SEIUSDT", "JUPUSDT", "WIFUSDT", "PEPEUSDT",
    "FETUSDT", "ICPUSDT", "HBARUSDT", "VETUSDT",
    "ARBUSDT", "OPUSDT", "INJUSDT", "SUIUSDT", "TIAUSDT",
]

TIMEFRAME      = "4H"
CHANNEL_PERIOD = 30
API_DELAY_SEC  = 0.15

# Entry thresholds
LONG_MAX_POS   = 25.0   # pos% <= 25 → LONG candidate
SHORT_MIN_POS  = 75.0   # pos% >= 75 → SHORT candidate

# Channel validity
MIN_WIDTH_PCT  = 3.0    # channel must be >= 3% wide
MAX_WIDTH_PCT  = 20.0   # channel must be <= 20% wide (too volatile = skip)

# BTC trend detection
BTC_TREND_LOOKBACK = 20  # candles for EMA20/50 comparison

OUTPUT_PATH = "data/pullback_setups.json"


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def _ohlc(c):
    if isinstance(c, dict):
        return (float(c.get("open", 0)), float(c.get("high", 0)),
                float(c.get("low", 0)), float(c.get("close", 0)))
    if isinstance(c, (list, tuple)) and len(c) >= 5:
        return float(c[1]), float(c[2]), float(c[3]), float(c[4])
    if hasattr(c, "high"):
        return (float(getattr(c, "open", 0)), float(c.high),
                float(c.low), float(c.close))
    return None, None, None, None


def ema(values, period):
    if len(values) < period:
        return None
    k = 2.0 / (period + 1)
    e = sum(values[:period]) / period
    for v in values[period:]:
        e = v * k + e * (1 - k)
    return e


def btc_direction(candles):
    """Return 'UP', 'DOWN', or 'FLAT'."""
    if len(candles) < 60:
        return "UNKNOWN"
    closes = [c["close"] if isinstance(c, dict) else c[4] for c in candles if c]
    closes = [float(c) for c in closes]
    e20 = ema(closes, 20)
    e50 = ema(closes, 50)
    if not e20 or not e50:
        return "UNKNOWN"
    diff_pct = (e20 - e50) / e50 * 100
    if diff_pct > 0.5:
        return "UP"
    if diff_pct < -0.5:
        return "DOWN"
    return "FLAT"


def compute_channel(candles, period=30):
    if len(candles) < period + 1:
        return None
    closed = candles[:-1]
    if len(closed) < period:
        return None
    window = closed[-period:]
    highs = []
    lows = []
    for c in window:
        h = c.get("high") if isinstance(c, dict) else c[2]
        l = c.get("low") if isinstance(c, dict) else c[3]
        highs.append(float(h))
        lows.append(float(l))
    upper = max(highs)
    lower = min(lows)
    mid = (upper + lower) / 2
    width = (upper - lower) / mid * 100 if mid > 0 else 0
    return {"upper": upper, "lower": lower, "mid": mid, "width_pct": round(width, 2)}


def last_candle_signature(candles):
    """Analyze last closed candle for pullback confirmation."""
    if len(candles) < 3:
        return None
    closed = candles[:-1]  # skip in-progress
    if len(closed) < 3:
        return None
    last = closed[-1]
    o, h, l, c = _ohlc(last)
    body = abs(c - o)
    range_ = h - l if h > l else 1e-9
    upper_wick = h - max(o, c)
    lower_wick = min(o, c) - l
    return {
        "bullish": c > o,
        "body_pct": round(body / range_ * 100, 1),
        "upper_wick_pct": round(upper_wick / range_ * 100, 1),
        "lower_wick_pct": round(lower_wick / range_ * 100, 1),
    }


def is_bullish_pullback(sig):
    """LONG pullback: bearish candle with long lower wick."""
    if not sig:
        return False
    return (not sig["bullish"] and sig["lower_wick_pct"] >= 30) or \
           (sig["lower_wick_pct"] >= 40)


def is_bearish_pullback(sig):
    """SHORT pullback: bullish candle with long upper wick."""
    if not sig:
        return False
    return (sig["bullish"] and sig["upper_wick_pct"] >= 30) or \
           (sig["upper_wick_pct"] >= 40)


def analyze_symbol(ex, symbol, btc_dir):
    try:
        candles = ex.get_historical_candles(symbol, TIMEFRAME, limit=CHANNEL_PERIOD + 10)
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}

    if not candles or len(candles) < CHANNEL_PERIOD + 1:
        return {"symbol": symbol, "error": "insufficient data"}

    ch = compute_channel(candles, CHANNEL_PERIOD)
    if not ch:
        return {"symbol": symbol, "error": "channel failed"}

    price = float(candles[-1].get("close") if isinstance(candles[-1], dict) else candles[-1][4])
    pos_pct = (price - ch["lower"]) / (ch["upper"] - ch["lower"]) * 100 if ch["upper"] > ch["lower"] else 50

    sig = last_candle_signature(candles)

    # ═══════════ VALIDATION CHAIN ═══════════

    # Layer 1: Channel width
    if ch["width_pct"] < MIN_WIDTH_PCT:
        return {"symbol": symbol, "reason": f"channel too narrow ({ch['width_pct']}%)",
                "error": None, "setup": None}
    if ch["width_pct"] > MAX_WIDTH_PCT:
        return {"symbol": symbol, "reason": f"channel too wide ({ch['width_pct']}%)",
                "error": None, "setup": None}

    # Layer 2: BTC direction filter
    setup = None
    setup_reason = None

    if btc_dir == "UP":
        # Only LONG allowed
        if pos_pct <= LONG_MAX_POS:
            if is_bullish_pullback(sig):
                setup = "LONG"
                setup_reason = "BTC UP + alt at bottom + bullish pullback"
            else:
                setup_reason = f"BTC UP, alt at bottom, waiting for pullback confirmation"
        else:
            setup_reason = f"BTC UP, alt not at bottom (pos={pos_pct:.0f}%)"

    elif btc_dir == "DOWN":
        # Only SHORT allowed
        if pos_pct >= SHORT_MIN_POS:
            if is_bearish_pullback(sig):
                setup = "SHORT"
                setup_reason = "BTC DOWN + alt at top + bearish pullback"
            else:
                setup_reason = f"BTC DOWN, alt at top, waiting for pullback confirmation"
        else:
            setup_reason = f"BTC DOWN, alt not at top (pos={pos_pct:.0f}%)"

    elif btc_dir == "FLAT":
        # Both directions allowed
        if pos_pct <= LONG_MAX_POS and is_bullish_pullback(sig):
            setup = "LONG"
            setup_reason = "BTC FLAT + alt at bottom + bullish pullback"
        elif pos_pct >= SHORT_MIN_POS and is_bearish_pullback(sig):
            setup = "SHORT"
            setup_reason = "BTC FLAT + alt at top + bearish pullback"
        else:
            setup_reason = f"BTC FLAT, no setup (pos={pos_pct:.0f}%)"

    # Calculate entry levels
    levels = None
    if setup == "LONG":
        sl = ch["lower"] * 0.992
        tp1 = ch["mid"]
        tp2 = ch["upper"]
        levels = {
            "entry": round(price, 8),
            "sl": round(sl, 8),
            "sl_pct": round((price - sl) / price * 100, 2),
            "tp1": round(tp1, 8),
            "tp1_pct": round((tp1 - price) / price * 100, 2),
            "tp2": round(tp2, 8),
            "tp2_pct": round((tp2 - price) / price * 100, 2),
        }
    elif setup == "SHORT":
        sl = ch["upper"] * 1.008
        tp1 = ch["mid"]
        tp2 = ch["lower"]
        levels = {
            "entry": round(price, 8),
            "sl": round(sl, 8),
            "sl_pct": round((sl - price) / price * 100, 2),
            "tp1": round(tp1, 8),
            "tp1_pct": round((price - tp1) / price * 100, 2),
            "tp2": round(tp2, 8),
            "tp2_pct": round((price - tp2) / price * 100, 2),
        }

    return {
        "symbol": symbol,
        "price": price,
        "pos_pct": round(pos_pct, 1),
        "channel": {k: round(v, 8) if isinstance(v, float) else v for k, v in ch.items()},
        "candle": sig,
        "setup": setup,
        "setup_reason": setup_reason,
        "levels": levels,
        "error": None,
    }


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def main():
    print("=" * 110)
    print(f"PULLBACK DETECTOR + BTC FILTER  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 110)

    ex = XTExchange(timeout=10)

    # Step 1: Determine BTC direction
    btc_candles = ex.get_historical_candles("BTCUSDT", TIMEFRAME, limit=100)
    btc_dir = btc_direction(btc_candles)

    btc_info = ""
    if btc_candles:
        btc_price = float(btc_candles[-1].get("close") if isinstance(btc_candles[-1], dict) else btc_candles[-1][4])
        btc_info = f"price={btc_price:.2f}"

    print(f"BTC DIRECTION: {btc_dir}  ({btc_info})")
    print()
    print(f"Allowed: ", end="")
    if btc_dir == "UP":
        print("LONG only (at channel bottom)")
    elif btc_dir == "DOWN":
        print("SHORT only (at channel top)")
    elif btc_dir == "FLAT":
        print("LONG at bottom OR SHORT at top")
    else:
        print("UNKNOWN — skipping analysis")
        return
    print("=" * 110)
    print()

    results = []
    for i, sym in enumerate(SYMBOLS, 1):
        if sym == "BTCUSDT":
            continue  # skip BTC itself
        r = analyze_symbol(ex, sym, btc_dir)
        results.append(r)
        if r.get("error"):
            print(f"  [{i:2d}/{len(SYMBOLS)}] {sym:12s}  ERROR: {r['error']}")
        elif r.get("setup"):
            print(f"  [{i:2d}/{len(SYMBOLS)}] {sym:12s}  ★ {r['setup']:5s}  pos={r['pos_pct']:5.1f}%  {r['setup_reason']}")
        else:
            print(f"  [{i:2d}/{len(SYMBOLS)}] {sym:12s}    -    pos={r.get('pos_pct', 0):5.1f}%  {r.get('reason', r.get('setup_reason', ''))}")
        time.sleep(API_DELAY_SEC)

    print()
    print("=" * 110)

    setups = [r for r in results if r.get("setup")]

    if setups:
        print(f"\n★ VALID SETUPS ({len(setups)}):\n")
        for r in setups:
            lv = r["levels"]
            c = r["channel"]
            print(f"  ━━━ {r['symbol']} — {r['setup']} ━━━")
            print(f"  BTC direction: {btc_dir}")
            print(f"  Alt channel pos: {r['pos_pct']}%")
            print(f"  Channel: {c['lower']:.6g} - {c['mid']:.6g} - {c['upper']:.6g} (width {c['width_pct']}%)")
            print(f"  Candle signature: wick_up={r['candle']['upper_wick_pct']}% wick_down={r['candle']['lower_wick_pct']}%")
            print(f"  ──────────────────────────────────")
            print(f"  Entry:  {lv['entry']:.6g}")
            print(f"  SL:     {lv['sl']:.6g}  ({lv['sl_pct']:+.2f}%)")
            print(f"  TP1:    {lv['tp1']:.6g}  ({lv['tp1_pct']:+.2f}%)")
            print(f"  TP2:    {lv['tp2']:.6g}  ({lv['tp2_pct']:+.2f}%)")
            print()
    else:
        print("\n⚠ NO VALID SETUPS today.")
        print(f"   BTC direction: {btc_dir}")
        print()
        print("   Closest candidates (near channel edges, but no pullback confirmation):")
        candidates = []
        for r in results:
            if r.get("error") or r.get("pos_pct") is None:
                continue
            if r["pos_pct"] <= 35 or r["pos_pct"] >= 65:
                candidates.append(r)
        candidates.sort(key=lambda x: min(x["pos_pct"], 100 - x["pos_pct"]))
        for r in candidates[:5]:
            side = "LOW" if r["pos_pct"] <= 50 else "HIGH"
            print(f"     {r['symbol']:12s} pos={r['pos_pct']:5.1f}% ({side})  {r.get('reason', '')}")

    # Export
    os.makedirs("data", exist_ok=True)
    snapshot = {
        "generated_at": datetime.now().isoformat(),
        "btc_direction": btc_dir,
        "valid_setups": setups,
        "all": [r for r in results if not r.get("error")],
    }
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, default=str)
    print(f"\nWrote snapshot → {OUTPUT_PATH}")
    print("=" * 110)


if __name__ == "__main__":
    main()