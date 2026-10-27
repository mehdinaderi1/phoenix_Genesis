"""
4H Donchian Channel Detector for Phoenix Genesis.
Identifies which symbols are at channel edges (best entry zones).
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
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
    "ZECUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT",
    "DOTUSDT", "POLUSDT", "NEARUSDT", "APTUSDT",
    "SEIUSDT", "JUPUSDT", "WIFUSDT", "PEPEUSDT",
    "FETUSDT", "ICPUSDT", "HBARUSDT", "VETUSDT",
    "ARBUSDT", "OPUSDT", "INJUSDT", "SUIUSDT", "TIAUSDT",
]

TIMEFRAME      = "4H"
CHANNEL_PERIOD = 30          # 30 x 4H = 5 days
EDGE_ZONE_PCT  = 1.0         # within 1% of edge = "at edge"
MIN_WIDTH_PCT  = 2.0         # channel must be >= 2% wide
API_DELAY_SEC  = 0.15

OUTPUT_PATH    = "data/channels.json"


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def _ohlc(c):
    """Return (high, low, close) from any candle format."""
    if isinstance(c, dict):
        return float(c.get("high", 0)), float(c.get("low", 0)), float(c.get("close", 0))
    if isinstance(c, (list, tuple)) and len(c) >= 5:
        return float(c[2]), float(c[3]), float(c[4])
    if hasattr(c, "high"):
        return float(c.high), float(c.low), float(getattr(c, "close", 0))
    return None, None, None


def compute_channel(candles, period=30):
    """Compute Donchian Channel from candles."""
    if len(candles) < period + 1:
        return None

    # Skip in-progress candle (last)
    closed = candles[:-1]
    if len(closed) < period:
        return None

    window = closed[-period:]
    highs = [_ohlc(c)[0] for c in window]
    lows = [_ohlc(c)[1] for c in window]

    if any(h is None for h in highs) or any(l is None for l in lows):
        return None

    upper = max(highs)
    lower = min(lows)
    mid = (upper + lower) / 2
    width_pct = (upper - lower) / mid * 100 if mid > 0 else 0

    return {
        "upper": round(upper, 8),
        "lower": round(lower, 8),
        "mid": round(mid, 8),
        "width_pct": round(width_pct, 2),
    }


def classify_position(price, upper, lower, edge_pct=1.0):
    """Classify where price is relative to channel."""
    if upper <= lower:
        return "unknown", None

    channel_range = upper - lower
    pos_pct = (price - lower) / channel_range * 100  # 0% = bottom, 100% = top

    # Distance from edges
    dist_from_top = (upper - price) / upper * 100
    dist_from_bottom = (price - lower) / lower * 100

    if dist_from_top <= edge_pct:
        return "top_edge", pos_pct
    elif dist_from_bottom <= edge_pct:
        return "bottom_edge", pos_pct
    elif pos_pct >= 70:
        return "upper_zone", pos_pct
    elif pos_pct <= 30:
        return "lower_zone", pos_pct
    else:
        return "mid", pos_pct


# ═══════════════════════════════════════════════════════════
# ANALYZE ONE SYMBOL
# ═══════════════════════════════════════════════════════════

def analyze_symbol(ex, symbol):
    try:
        candles = ex.get_historical_candles(symbol, TIMEFRAME, limit=CHANNEL_PERIOD + 10)
    except Exception as e:
        return {"symbol": symbol, "error": f"fetch failed: {e}"}

    if not candles or len(candles) < CHANNEL_PERIOD + 1:
        return {"symbol": symbol, "error": f"insufficient data ({len(candles) if candles else 0})"}

    channel = compute_channel(candles, CHANNEL_PERIOD)
    if not channel:
        return {"symbol": symbol, "error": "channel computation failed"}

    # Current price = last close
    _, _, price = _ohlc(candles[-1])
    if price is None:
        return {"symbol": symbol, "error": "no price"}

    position, pos_pct = classify_position(
        price, channel["upper"], channel["lower"], EDGE_ZONE_PCT
    )

    # Tradeable?
    tradeable = False
    setup = None
    reason = None

    if channel["width_pct"] < MIN_WIDTH_PCT:
        reason = f"channel too narrow ({channel['width_pct']}%)"
    elif position == "top_edge":
        tradeable = True
        setup = "SHORT"
    elif position == "bottom_edge":
        tradeable = True
        setup = "LONG"
    elif position == "upper_zone":
        reason = "near top but not at edge"
    elif position == "lower_zone":
        reason = "near bottom but not at edge"
    else:
        reason = "mid-channel"

    return {
        "symbol": symbol,
        "price": price,
        "channel": channel,
        "position": position,
        "pos_pct": round(pos_pct, 1) if pos_pct is not None else None,
        "tradeable": tradeable,
        "setup": setup,
        "reason": reason,
        "error": None,
    }


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def main():
    print("=" * 110)
    print(f"4H CHANNEL DETECTOR  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Symbols: {len(SYMBOLS)}  |  TF: {TIMEFRAME}  |  Period: {CHANNEL_PERIOD}  |  "
          f"Edge: {EDGE_ZONE_PCT}%  |  MinWidth: {MIN_WIDTH_PCT}%")
    print("=" * 110)

    ex = XTExchange(timeout=10)
    results = []

    for i, sym in enumerate(SYMBOLS, 1):
        r = analyze_symbol(ex, sym)
        results.append(r)
        if r.get("error"):
            print(f"  [{i:2d}/{len(SYMBOLS)}] {sym:12s}  ERROR: {r['error']}")
        else:
            marker = ""
            if r["tradeable"]:
                marker = f"  ★ {r['setup']}"
            print(f"  [{i:2d}/{len(SYMBOLS)}] {sym:12s}  "
                  f"{r['position']:12s}  "
                  f"pos={r['pos_pct']:5.1f}%{marker}")
        time.sleep(API_DELAY_SEC)

    print()
    print("─" * 110)
    print(f"{'SYMBOL':12s} {'POSITION':14s} {'POS%':>6s} {'PRICE':>14s} "
          f"{'LOWER':>14s} {'MID':>14s} {'UPPER':>14s} {'WIDTH':>7s} {'SETUP':>8s}")
    print("─" * 110)

    valid = [r for r in results if not r.get("error")]
    # Sort: tradeable first, then by pos_pct (extreme first)
    valid.sort(key=lambda x: (
        0 if x["tradeable"] else 1,
        min(x["pos_pct"] or 50, 100 - (x["pos_pct"] or 50))
    ))

    for r in valid:
        c = r["channel"]
        print(
            f"{r['symbol']:12s} {r['position']:14s} {r['pos_pct']:6.1f} "
            f"{r['price']:>14.8g} {c['lower']:>14.8g} {c['mid']:>14.8g} "
            f"{c['upper']:>14.8g} {c['width_pct']:>6.2f}% "
            f"{r['setup'] or '-':>8s}"
        )

    print()
    print("=" * 110)

    # Tradeable setups
    tradeables = [r for r in valid if r["tradeable"]]
    if tradeables:
        print(f"★ TRADEABLE SETUPS ({len(tradeables)}):")
        for r in tradeables:
            c = r["channel"]
            if r["setup"] == "LONG":
                sl = c["lower"] * 0.992
                print(f"  → {r['symbol']:12s} LONG at {r['price']:.6g}  "
                      f"SL={sl:.6g} (-0.8%)  Channel: {c['lower']:.6g}-{c['upper']:.6g}")
            else:
                sl = c["upper"] * 1.008
                print(f"  → {r['symbol']:12s} SHORT at {r['price']:.6g}  "
                      f"SL={sl:.6g} (+0.8%)  Channel: {c['lower']:.6g}-{c['upper']:.6g}")
    else:
        print("★ NO TRADEABLE SETUPS — all symbols mid-channel or invalid")
        # Show nearest to edge
        nearest = sorted(valid, key=lambda x: min(
            (x["price"] - x["channel"]["lower"]) / x["channel"]["lower"] * 100,
            (x["channel"]["upper"] - x["price"]) / x["channel"]["upper"] * 100,
        ))[:3]
        print()
        print("  Nearest to edge:")
        for r in nearest:
            c = r["channel"]
            dist_top = (c["upper"] - r["price"]) / c["upper"] * 100
            dist_bot = (r["price"] - c["lower"]) / c["lower"] * 100
            print(f"    {r['symbol']:12s}  "
                  f"top: {dist_top:+.2f}%  bottom: {dist_bot:+.2f}%")

    # Export
    os.makedirs("data", exist_ok=True)
    snapshot = {
        "generated_at": datetime.now().isoformat(),
        "period": CHANNEL_PERIOD,
        "timeframe": TIMEFRAME,
        "tradeable": [
            {
                "symbol": r["symbol"],
                "setup": r["setup"],
                "price": r["price"],
                "channel": r["channel"],
                "pos_pct": r["pos_pct"],
            }
            for r in tradeables
        ],
        "all": [
            {k: v for k, v in r.items() if k != "error"}
            for r in valid
        ],
    }
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, default=str)
    print(f"\nWrote snapshot → {OUTPUT_PATH}")

    errors = [r for r in results if r.get("error")]
    if errors:
        print(f"\nERRORS: {len(errors)}")
        for r in errors:
            print(f"  ! {r['symbol']:12s} {r['error']}")

    print("=" * 110)


if __name__ == "__main__":
    main()