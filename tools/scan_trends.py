"""
Trend Scanner for Phoenix Genesis.
Scans multiple symbols on XT and ranks by trend strength.
Writes both human-readable table and data/watchlist.json.
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
    "DOTUSDT", "POLUSDT", "NEARUSDT", "APTUSDT","FTMUSDT",
    "SEIUSDT", "JUPUSDT", "WIFUSDT", "PEPEUSDT",
    "RNDRUSDT", "FETUSDT", "ICPUSDT", "HBARUSDT", "VETUSDT",
    "ARBUSDT", "OPUSDT", "INJUSDT", "SUIUSDT", "TIAUSDT",
]

PRIMARY_TF      = "1H"
MTF_TFS         = ["5m", "1H", "1D"]
CANDLE_LIMIT    = 300
API_DELAY_SEC   = 0.15          # rate-limit protection between symbol scans

# Score thresholds
SCORE_ELIGIBLE  = 60            # >= eligible for active watching
SCORE_WATCHLIST = 40            # >= watchlist
ADX_STRONG      = 40
ADX_ACTIVE      = 25
FRESH_BARS      = 20            # <= 20 bars (10h on 1H) = fresh trend

WATCHLIST_PATH  = "data/watchlist.json"


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def _ohlc(c):
    """Return (high, low, close, volume) from any candle format."""
    if isinstance(c, dict):
        return (
            float(c.get("high", 0)),
            float(c.get("low", 0)),
            float(c.get("close", 0)),
            float(c.get("volume", 0)),
        )
    if isinstance(c, (list, tuple)) and len(c) >= 6:
        return float(c[2]), float(c[3]), float(c[4]), float(c[5])
    if hasattr(c, "high"):
        return (
            float(c.high),
            float(c.low),
            float(getattr(c, "close", 0)),
            float(getattr(c, "volume", 0)),
        )
    return None, None, None, None


def ema(values, period):
    if len(values) < period:
        return []
    k = 2.0 / (period + 1)
    out = [sum(values[:period]) / period]
    for v in values[period:]:
        out.append(v * k + out[-1] * (1 - k))
    return out


def adx(candles, period=14):
    """ADX (Wilder). Returns last value or None."""
    if len(candles) < period * 2 + 1:
        return None
    tr_list, plus_dm, minus_dm = [], [], []
    for i in range(1, len(candles)):
        h, l, _, _ = _ohlc(candles[i])
        h_prev, l_prev, c_prev, _ = _ohlc(candles[i - 1])
        if None in (h, l, c_prev, h_prev, l_prev):
            return None
        tr = max(h - l, abs(h - c_prev), abs(l - c_prev))
        up = h - h_prev
        dn = l_prev - l
        plus_dm.append(up if (up > dn and up > 0) else 0.0)
        minus_dm.append(dn if (dn > up and dn > 0) else 0.0)
        tr_list.append(tr)

    atr = sum(tr_list[:period]) / period
    pdi_s = sum(plus_dm[:period]) / period
    mdi_s = sum(minus_dm[:period]) / period
    dx_list = []
    for i in range(period, len(tr_list)):
        atr = (atr * (period - 1) + tr_list[i]) / period
        pdi_s = (pdi_s * (period - 1) + plus_dm[i]) / period
        mdi_s = (mdi_s * (period - 1) + minus_dm[i]) / period
        if atr <= 0:
            continue
        pdi = 100 * pdi_s / atr
        mdi = 100 * mdi_s / atr
        denom = pdi + mdi
        if denom <= 0:
            continue
        dx_list.append(100 * abs(pdi - mdi) / denom)

    if len(dx_list) < period:
        return None
    adx_val = sum(dx_list[:period]) / period
    for dx in dx_list[period:]:
        adx_val = (adx_val * (period - 1) + dx) / period
    return adx_val


def slope_pct(values, window=10):
    if len(values) < window:
        return None
    first = values[-window]
    last = values[-1]
    if first <= 0:
        return None
    return (last - first) / first * 100


def trend_direction(closes, fast=20, slow=50):
    if len(closes) < slow + 5:
        return "unknown"
    e20 = ema(closes, fast)
    e50 = ema(closes, slow)
    if not e20 or not e50:
        return "unknown"
    diff = (e20[-1] - e50[-1]) / e50[-1] * 100
    if diff > 0.3:
        return "up"
    if diff < -0.3:
        return "down"
    return "flat"


def trend_age_bars(closes, fast=20, slow=50, max_look=120):
    """Bars since EMA20/50 last crossed. Capped at max_look."""
    if len(closes) < slow + 5:
        return None
    e20 = ema(closes, fast)
    e50 = ema(closes, slow)
    offset = len(e20) - len(e50)
    if offset < 0:
        return None
    n = min(len(e20) - offset, len(e50), max_look + 1)
    if n < 5:
        return None
    current_sign = 1 if (e20[-1] - e50[-1]) > 0 else -1
    for i in range(2, n):
        prev_sign = 1 if (e20[-i] - e50[-i]) > 0 else -1
        if prev_sign != current_sign:
            return i - 1
    return max_look


def volume_ratio(candles, window=20):
    vols = []
    for c in candles:
        _, _, _, v = _ohlc(c)
        if v and v > 0:
            vols.append(v)
    if len(vols) < window + 1:
        return None
    # Skip last candle (in-progress, near-zero volume)
    closed_vols = vols[:-1]
    if len(closed_vols) < window:
        return None
    avg = sum(closed_vols[-window:]) / window
    if avg <= 0:
        return None
    return closed_vols[-1] / avg

def hot_score(candles_1h):
    """Compute 'hot' score 0-30 from 24h momentum and volume surge (closed candles only)."""
    if len(candles_1h) < 169:
        return {"hot_score": 0, "change_24h": None, "vol_ratio_7d": None}

    closed = candles_1h[:-1]   # skip in-progress
    if len(closed) < 168:
        return {"hot_score": 0, "change_24h": None, "vol_ratio_7d": None}

    last_24 = closed[-24:]
    first_close = _ohlc(last_24[0])[2]
    last_close = _ohlc(last_24[-1])[2]
    change_24h = (last_close - first_close) / first_close * 100 if first_close else 0

    vol_24h = sum(_ohlc(c)[3] for c in last_24)
    vol_7d_avg_24h = sum(_ohlc(c)[3] for c in closed) / len(closed) * 24
    vol_ratio_7d = vol_24h / vol_7d_avg_24h if vol_7d_avg_24h > 0 else None

    score = 0
    # Realistic thresholds for current market (low volatility)
    if abs(change_24h) >= 5:    score += 10
    elif abs(change_24h) >= 2:  score += 5

    if vol_ratio_7d is not None:
        if vol_ratio_7d >= 2.0:   score += 10
        elif vol_ratio_7d >= 1.3: score += 5

    return {
        "hot_score":    score,
        "change_24h":   round(change_24h, 2),
        "vol_ratio_7d": round(vol_ratio_7d, 2) if vol_ratio_7d else None,
    }


# ═══════════════════════════════════════════════════════════
# SCORE ONE SYMBOL
# ═══════════════════════════════════════════════════════════

def score_symbol(ex, symbol):
    try:
        candles_1h = ex.get_historical_candles(symbol, PRIMARY_TF, limit=CANDLE_LIMIT)
    except Exception as e:
        return {"symbol": symbol, "error": f"fetch failed: {e}"}

    if not candles_1h or len(candles_1h) < 200:
        return {"symbol": symbol,
                "error": f"insufficient history ({len(candles_1h) if candles_1h else 0})"}

    closes = []
    for c in candles_1h:
        _, _, cl, _ = _ohlc(c)
        if cl is not None:
            closes.append(cl)
    if len(closes) < 200:
        return {"symbol": symbol, "error": "not enough closes"}

    # ADX
    adx_val = adx(candles_1h)
    adx_score = 0
    if adx_val is not None:
        if adx_val >= ADX_STRONG:         adx_score = 30
        elif adx_val >= 30:               adx_score = 25
        elif adx_val >= ADX_ACTIVE:       adx_score = 15
        elif adx_val >= 20:               adx_score = 5

    # EMA200 distance
    e200 = ema(closes, 200)
    e200_dist = (closes[-1] - e200[-1]) / e200[-1] * 100 if e200 else 0
    ema_score = 0
    if abs(e200_dist) >= 10:      ema_score = 20
    elif abs(e200_dist) >= 5:     ema_score = 15
    elif abs(e200_dist) >= 2:     ema_score = 8

    # EMA20 slope
    e20 = ema(closes, 20)
    slope = slope_pct(e20, 10) if e20 else None
    slope_score = 0
    if slope is not None:
        if abs(slope) >= 2.0:         slope_score = 20
        elif abs(slope) >= 1.0:       slope_score = 15
        elif abs(slope) >= 0.5:       slope_score = 8
        elif abs(slope) >= 0.1:       slope_score = 3

    # MTF agreement
    direction_1h = trend_direction(closes)
    votes = [direction_1h]
    for tf in ["5m", "1D"]:
        try:
            cs = ex.get_historical_candles(symbol, tf, limit=120)
            if cs and len(cs) > 60:
                cl = [float(_ohlc(c)[2]) for c in cs if _ohlc(c)[2] is not None]
                votes.append(trend_direction(cl))
            else:
                votes.append("unknown")
        except Exception:
            votes.append("unknown")

    up_votes = votes.count("up")
    down_votes = votes.count("down")
    if up_votes == 3:
        mtf_score, mtf_dir = 20, "up"
    elif down_votes == 3:
        mtf_score, mtf_dir = 20, "down"
    elif up_votes == 2:
        mtf_score, mtf_dir = 10, "up"
    elif down_votes == 2:
        mtf_score, mtf_dir = 10, "down"
    else:
        mtf_score, mtf_dir = 0, "mixed"

    # Volume
    vr = volume_ratio(candles_1h)
    vol_score = 0
    if vr is not None:
        if vr >= 1.5:     vol_score = 10
        elif vr >= 1.2:   vol_score = 6
        elif vr >= 1.0:   vol_score = 2

    hot = hot_score(candles_1h)

    # Freshness
    age = trend_age_bars(closes)
    if age is None:
        fresh_score, fresh_label = 0, "unknown"
    elif age <= FRESH_BARS:
        fresh_score, fresh_label = 20, "fresh"
    elif age <= 60:
        fresh_score, fresh_label = 12, "recent"
    elif age <= 120:
        fresh_score, fresh_label = 5, "aging"
    else:
        fresh_score, fresh_label = 0, "stale"

    total = adx_score + ema_score + slope_score + mtf_score + vol_score + fresh_score
    direction = mtf_dir if mtf_dir != "mixed" else direction_1h

    return {
        "symbol":         symbol,
        "score":          total,
        "direction":      direction,
        "adx":            round(adx_val, 1) if adx_val else None,
        "ema200_dist":    round(e200_dist, 2),
        "slope":          round(slope, 2) if slope else None,
        "mtf_votes":      votes,
        "vol_ratio":      round(vr, 2) if vr else None,
        "age_bars":       age,
        "freshness":      fresh_label,
        "price":          closes[-1],
        "hot_score":    hot["hot_score"],
        "change_24h":   hot["change_24h"],
        "vol_ratio_7d": hot["vol_ratio_7d"],
        "subscores": {
            "adx": adx_score, "ema": ema_score, "slope": slope_score,
            "mtf": mtf_score, "vol": vol_score, "fresh": fresh_score,
        },
        "error": None,
    }


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def main():
    print("=" * 105)
    print(f"TREND SCANNER  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Symbols: {len(SYMBOLS)}  |  Primary TF: {PRIMARY_TF}  |  MTF: {', '.join(MTF_TFS)}")
    print("=" * 105)

    ex = XTExchange(timeout=10)
    results = []

    for i, sym in enumerate(SYMBOLS, 1):
        r = score_symbol(ex, sym)
        results.append(r)
        if r.get("error"):
            print(f"  [{i:2d}/{len(SYMBOLS)}] {sym:12s}  ERROR: {r['error']}")
        else:
            print(f"  [{i:2d}/{len(SYMBOLS)}] {sym:12s}  score={r['score']:3d}  "
                  f"dir={r['direction']:>5s}  fresh={r['freshness']}")
            # ─── WARNING ───
            if (r["freshness"] == "fresh"
                    and r["vol_ratio"] is not None
                    and r["vol_ratio"] < 1.0):
                print(f"           ⚠ fresh but low volume "
                      f"({r['vol_ratio']}x) — unconfirmed")
        time.sleep(API_DELAY_SEC)

    print()
    print("─" * 105)
    header = (f"{'SYMBOL':12s} {'SCORE':>5s} {'HOT':>4s} {'DIR':>6s} {'FRESH':>8s} "
              f"{'AGE':>4s} {'ADX':>5s} {'CHG24':>8s} {'PRICE':>12s}")
    print(header)
    print("─" * 105)

    valid = [r for r in results if not r.get("error")]
    valid.sort(key=lambda x: -x["score"])

    for r in valid:
        print(
            f"{r['symbol']:12s} {r['score']:5d} {r['hot_score']:4d} "
            f"{r['direction']:>6s} {r['freshness']:>8s} "
            f"{str(r['age_bars'] if r['age_bars'] is not None else '-'):>4s} "
            f"{str(r['adx'] if r['adx'] is not None else '-'):>5s} "
            f"{str(r['change_24h'] if r['change_24h'] is not None else '-'):>8s} "
            f"{r['price']:>12.2f}"
        )

    print()
    print("=" * 105)

    eligible = [r for r in valid if r["score"] >= SCORE_ELIGIBLE]
    watchlist = [r for r in valid if SCORE_WATCHLIST <= r["score"] < SCORE_ELIGIBLE]

    print(f"ELIGIBLE (score >= {SCORE_ELIGIBLE}):  {len(eligible)}")
    # ─── WARNINGS ───
    warnings = [
        r for r in valid
        if r["freshness"] == "fresh"
        and r["vol_ratio"] is not None
        and r["vol_ratio"] < 1.0
    ]
    if warnings:
        print(f"\n⚠ WARNINGS ({len(warnings)} fresh but unconfirmed):")
        for r in warnings:
            print(f"  · {r['symbol']:12s} score={r['score']:3d}  "
                  f"ADX={r['adx']}  vol={r['vol_ratio']}x  — low volume")
    for r in eligible:
        print(f"  → {r['symbol']:12s} {r['direction'].upper():4s}  "
              f"score={r['score']}  freshness={r['freshness']}  age={r['age_bars']}b")

    print(f"\nWATCHLIST ({SCORE_WATCHLIST}-{SCORE_ELIGIBLE-1}):  {len(watchlist)}")
    for r in watchlist:
        print(f"  · {r['symbol']:12s} {r['direction'].upper():4s}  "
              f"score={r['score']}  hot={r['hot_score']}  "
              f"freshness={r['freshness']}")

    # Export JSON
    os.makedirs("data", exist_ok=True)
    snapshot = {
        "generated_at": datetime.now().isoformat(),
        "eligible": [
            {"symbol": r["symbol"], "score": r["score"],
             "direction": r["direction"], "freshness": r["freshness"],
             "age_bars": r["age_bars"], "price": r["price"]}
            for r in eligible
        ],
        "watchlist": [
            {"symbol": r["symbol"], "score": r["score"],
             "direction": r["direction"], "freshness": r["freshness"]}
            for r in watchlist
        ],
        "all": [
            {k: v for k, v in r.items() if k != "subscores"}
            for r in valid
        ],
    }
    with open(WATCHLIST_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, default=str)
    print(f"\nWrote snapshot → {WATCHLIST_PATH}")

    errors = [r for r in results if r.get("error")]
    if errors:
        print(f"\nERRORS: {len(errors)}")
        for r in errors:
            print(f"  ! {r['symbol']:12s} {r['error']}")

    print("=" * 105)


if __name__ == "__main__":
    main()