"""
tools/break_retest_detector.py — READ-ONLY break-and-retest detector

Detects two classic patterns:
  1. Breakdown-Retest SHORT: 4H channel floor broken, 1H retest as resistance
  2. Breakout-Retest LONG:   4H channel ceiling broken, 1H retest as support

Channel: 4H Donchian (30)  |  Trigger: 1H closed candles
No orders. No state changes. Safe to run alongside Runner.

Usage:
    python tools/break_retest_detector.py
    python tools/break_retest_detector.py --verbose
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exchanges.xt_exchange import XTExchange
from tools.futures_strategy_runner import (
    SYMBOLS, TIMEFRAME, CHANNEL_PERIOD,
    compute_channel, btc_direction, candle_sig_with_volume,
    _close, _high, _low,
)

# ═══════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════
TIMEFRAME_TRIGGER = "1H"      # break+retest detection on 1H closed candles
BREAK_WINDOW      = 12        # look back N closed 1H candles for the break (12h)
MIN_BREAK_AGE     = 2         # break must be ≥N closed 1H candles old (2h)
MIN_BREAK_DEPTH   = 0.005     # break close must be ≥0.5% beyond level
RETEST_ZONE_BD    = (0.98, 1.03)  # floor  × [low, high]
RETEST_ZONE_BO    = (0.97, 1.02)  # ceiling × [low, high]
REJECTION_WICK    = 30.0      # min wick % for rejection
SL_BUFFER         = 0.005     # 0.5% SL buffer
TP_BUFFER         = 0.005     # 0.5% TP buffer
MIN_RR            = 1.0       # reject if R:R below


def _check_breakdown_retest(candles, ch, sig, btc_dir):
    """Breakdown-Retest SHORT. candles/sig are from trigger TF (1H)."""
    if not candles or len(candles) < BREAK_WINDOW + 5:
        return None, "short_data"
    if not ch or not sig:
        return None, "no_channel_or_sig"

    closed = candles[:-1]
    price  = _close(candles[-1])
    floor  = ch["lower"]
    width  = ch["upper"] - floor
    if width <= 0:
        return None, "zero_width"

    recent = closed[-BREAK_WINDOW:]

    break_idx = None
    for i in range(len(recent) - 1, -1, -1):
        if _close(recent[i]) < floor * (1 - MIN_BREAK_DEPTH):
            break_idx = i; break
    if break_idx is None:
        return None, f"no_break(close<{floor*(1-MIN_BREAK_DEPTH):.4g})"
    if break_idx > len(recent) - 1 - MIN_BREAK_AGE:
        return None, f"break_too_fresh({len(recent)-1-break_idx}<{MIN_BREAK_AGE})"

    deepest_low = min(_low(c) for c in recent[break_idx:])

    lo, hi = RETEST_ZONE_BD
    zone_lo, zone_hi = floor * lo, floor * hi
    if price < zone_lo:
        return None, f"below_zone({price:.4g}<{zone_lo:.4g})"
    if price > zone_hi:
        return None, f"above_zone({price:.4g}>{zone_hi:.4g})"
    if price <= deepest_low * 1.005:
        return None, f"no_bounce(price≤{deepest_low*1.005:.4g})"

    bearish    = (not sig["bullish"]) and sig["volume_confirmed"]
    upper_wick = sig["upper_wick_pct"] >= REJECTION_WICK and sig["volume_confirmed"]
    if not (bearish or upper_wick):
        return None, f"no_rejection(vol={sig.get('volume_ratio',0):.2f}, uw={sig.get('upper_wick_pct',0):.1f}%)"

    if btc_dir == "UP":
        return None, "btc_up"

    recent_high = max(_high(c) for c in recent[-3:])
    sl = recent_high * (1 + SL_BUFFER)
    tp = deepest_low * (1 + TP_BUFFER)
    if not (sl > price > tp):
        return None, f"invalid_sl_tp(sl={sl:.4g},price={price:.4g},tp={tp:.4g})"
    rr = (price - tp) / (sl - price) if (sl - price) > 0 else 0
    if rr < MIN_RR:
        return None, f"rr_low({rr:.2f}<{MIN_RR})"

    return {
        "setup_type": "breakdown_retest", "side": "SHORT",
        "pos_pct": (price - floor) / width * 100,
        "sl": sl, "tp": tp, "price": price, "rr": rr,
        "break_ago": len(recent) - 1 - break_idx,
        "volume_ratio": sig.get("volume_ratio", 0),
    }, "hit"


def _check_breakout_retest(candles, ch, sig, btc_dir):
    """Breakout-Retest LONG. candles/sig are from trigger TF (1H)."""
    if not candles or len(candles) < BREAK_WINDOW + 5:
        return None, "short_data"
    if not ch or not sig:
        return None, "no_channel_or_sig"

    closed  = candles[:-1]
    price   = _close(candles[-1])
    floor   = ch["lower"]
    ceiling = ch["upper"]
    width   = ceiling - floor
    if width <= 0:
        return None, "zero_width"

    recent = closed[-BREAK_WINDOW:]

    break_idx = None
    for i in range(len(recent) - 1, -1, -1):
        if _close(recent[i]) > ceiling * (1 + MIN_BREAK_DEPTH):
            break_idx = i; break
    if break_idx is None:
        return None, f"no_break(close>{ceiling*(1+MIN_BREAK_DEPTH):.4g})"
    if break_idx > len(recent) - 1 - MIN_BREAK_AGE:
        return None, f"break_too_fresh({len(recent)-1-break_idx}<{MIN_BREAK_AGE})"

    highest_high = max(_high(c) for c in recent[break_idx:])

    lo, hi = RETEST_ZONE_BO
    zone_lo, zone_hi = ceiling * lo, ceiling * hi
    if price < zone_lo:
        return None, f"below_zone({price:.4g}<{zone_lo:.4g})"
    if price > zone_hi:
        return None, f"above_zone({price:.4g}>{zone_hi:.4g})"
    if price >= highest_high * 0.995:
        return None, f"no_pullback(price≥{highest_high*0.995:.4g})"

    bullish    = sig["bullish"] and sig["volume_confirmed"]
    lower_wick = sig["lower_wick_pct"] >= REJECTION_WICK and sig["volume_confirmed"]
    if not (bullish or lower_wick):
        return None, f"no_rejection(vol={sig.get('volume_ratio',0):.2f}, lw={sig.get('lower_wick_pct',0):.1f}%)"

    if btc_dir == "DOWN":
        return None, "btc_down"

    recent_low = min(_low(c) for c in recent[-3:])
    sl = recent_low * (1 - SL_BUFFER)
    tp = highest_high * (1 - TP_BUFFER)
    if not (sl < price < tp):
        return None, f"invalid_sl_tp(sl={sl:.4g},price={price:.4g},tp={tp:.4g})"
    rr = (tp - price) / (price - sl) if (price - sl) > 0 else 0
    if rr < MIN_RR:
        return None, f"rr_low({rr:.2f}<{MIN_RR})"

    return {
        "setup_type": "breakout_retest", "side": "LONG",
        "pos_pct": (price - floor) / width * 100,
        "sl": sl, "tp": tp, "price": price, "rr": rr,
        "break_ago": len(recent) - 1 - break_idx,
        "volume_ratio": sig.get("volume_ratio", 0),
    }, "hit"


def detect_break_retest(candles, ch, sig, btc_dir):
    hit, r1 = _check_breakdown_retest(candles, ch, sig, btc_dir)
    if hit: return hit, r1
    hit, r2 = _check_breakout_retest(candles, ch, sig, btc_dir)
    if hit: return hit, r2
    return None, f"BD:{r1} | BO:{r2}"


def main(verbose=False):
    spot = XTExchange(timeout=15)
    print(f"[BR] Channel TF: {TIMEFRAME}  |  Trigger TF: {TIMEFRAME_TRIGGER}")
    print("[BR] fetching BTC direction...")
    try:
        btc_dir = btc_direction(spot.get_historical_candles("BTCUSDT", TIMEFRAME, limit=100))
    except Exception as e:
        btc_dir = f"ERR({e})"
    print(f"[BR] BTC = {btc_dir}\n")
    
    hits, misses, failed = [], [], []
    watchlist_fresh, watchlist_retest, watchlist_bounce = [], [], []
    for sym in SYMBOLS:
        # ── 4H channel ──
        try:
            candles_4h = spot.get_historical_candles(sym, TIMEFRAME, limit=CHANNEL_PERIOD + 20)
        except Exception as e:
            failed.append((sym, f"4H:{str(e)[:40]}")); continue
        if not candles_4h or len(candles_4h) < CHANNEL_PERIOD + 5:
            failed.append((sym, "short_4H")); continue
        ch = compute_channel(candles_4h, CHANNEL_PERIOD)
        if not ch:
            failed.append((sym, "no_channel")); continue

        # ── 1H trigger ──
        try:
            candles_1h = spot.get_historical_candles(sym, TIMEFRAME_TRIGGER, limit=BREAK_WINDOW + 20)
        except Exception as e:
            failed.append((sym, f"1H:{str(e)[:40]}")); continue
        if not candles_1h or len(candles_1h) < BREAK_WINDOW + 5:
            failed.append((sym, "short_1H")); continue
        sig = candle_sig_with_volume(candles_1h, window=10)
        if not sig:
            failed.append((sym, "no_sig")); continue

        hit, reason = detect_break_retest(candles_1h, ch, sig, btc_dir)
        price = _close(candles_1h[-1])
        if hit:
            hit["symbol"] = sym; hits.append(hit)
        else:
            entry = {
                "symbol": sym, "price": price, "reason": reason,
                "pos": (price - ch["lower"]) / (ch["upper"] - ch["lower"]) * 100
                        if ch["upper"] > ch["lower"] else 0,
            }
            misses.append(entry)

            # ── Watchlist classification ──
            r_all = reason  # "BD:... | BO:..."
            if "break_too_fresh" in r_all:
                watchlist_fresh.append(entry)
            elif "no_rejection" in r_all and "below_zone" not in r_all and "above_zone" not in r_all:
                watchlist_retest.append(entry)
            elif "no_bounce" in r_all or "no_pullback" in r_all:
                watchlist_bounce.append(entry)
        time.sleep(0.25)

    print("=" * 110)
    if hits:
        print(f"🎯 {len(hits)} BREAK-RETEST SETUP(S) FOUND\n")
        print(f"{'SYMBOL':11s} {'TYPE':17s} {'SIDE':5s} {'PRICE':>11s} {'SL':>11s} "
              f"{'TP':>11s} {'R:R':>5s} {'POS%':>6s} {'VOL':>5s} {'AGE':>4s}")
        print("-" * 110)
        for h in hits:
            print(f"{h['symbol']:11s} {h['setup_type']:17s} {h['side']:5s} "
                  f"{h['price']:>11.6g} {h['sl']:>11.6g} {h['tp']:>11.6g} "
                  f"{h['rr']:>5.2f} {h['pos_pct']:>6.1f} {h['volume_ratio']:>5.2f} {h['break_ago']:>4d}")
    else:
        print("❌ No break-retest setups today.")

    if verbose and misses:
        print("\n" + "─" * 110)
        print("Rejection reasons (sorted by distance from floor/ceiling):")
        print(f"{'SYMBOL':11s} {'PRICE':>11s} {'POS%':>6s}  REASON")
        print("-" * 110)
        misses.sort(key=lambda r: abs(r["pos"]))
        for r in misses[:20]:
            print(f"{r['symbol']:11s} {r['price']:>11.6g} {r['pos']:>6.1f}  {r['reason']}")

    print(f"\nSummary: hits={len(hits)} no_hit={len(misses)} failed={len(failed)}")
    # ═══════════════════════════════════════════════════════
    # WATCHLIST — what's about to become a setup
    # ═══════════════════════════════════════════════════════
    if watchlist_fresh or watchlist_retest or watchlist_bounce:
        print("\n" + "═" * 110)
        print("👀 WATCHLIST — imminent setups\n")

    if watchlist_fresh:
        print(f"🆕 FRESH BREAK — {len(watchlist_fresh)} symbol(s), break <2h old, waiting for retest:")
        print(f"   {'SYMBOL':11s} {'PRICE':>11s} {'POS%':>7s}  NEXT: wait for price to return to level")
        for r in sorted(watchlist_fresh, key=lambda x: x["pos"]):
            print(f"   {r['symbol']:11s} {r['price']:>11.6g} {r['pos']:>7.1f}")
        print()

    if watchlist_retest:
        print(f"🎯 RETEST IN PROGRESS — {len(watchlist_retest)} symbol(s), price at level, waiting for rejection candle:")
        print(f"   {'SYMBOL':11s} {'PRICE':>11s} {'POS%':>7s}  NEXT: watch next 1H candle for rejection+volume")
        for r in sorted(watchlist_retest, key=lambda x: abs(x["pos"])):
            print(f"   {r['symbol']:11s} {r['price']:>11.6g} {r['pos']:>7.1f}")
        print()

    if watchlist_bounce:
        print(f"⏳ BOUNCED BACK — {len(watchlist_bounce)} symbol(s), broke then bounced, waiting for 2nd break:")
        print(f"   {'SYMBOL':11s} {'PRICE':>11s} {'POS%':>7s}  NEXT: watch for re-break of level")
        for r in sorted(watchlist_bounce, key=lambda x: abs(x["pos"])):
            print(f"   {r['symbol']:11s} {r['price']:>11.6g} {r['pos']:>7.1f}")
        print()
    for s, e in failed:
        print(f"  FAIL {s}: {e}")


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    main(verbose=verbose)