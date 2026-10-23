"""
Comprehensive strategy × timeframe × fee scan.
Definitively answers: is ANY simple strategy profitable on BTC?

Tests:
- RSI mean-reversion on 5m, 15m, 30m
- EMA cross trend-following on 5m, 15m, 30m
- With fee 0.12% (taker) and 0.04% (maker)
- Per-stretch backtest (RSI resets at gaps)
- Minimum 200 candles per stretch for EMA warmup
"""
import json
import sqlite3
from pathlib import Path
from itertools import product

DB = Path("data/phoenix.db")
SYMBOL = "BTCUSDT"

FEES = [0.0012, 0.0004]
TIMEFRAMES = ["5m", "15m", "30m"]
MIN_STRETCH = 250


def load_candles(tf):
    conn = sqlite3.connect(str(DB))
    rows = conn.execute(
        "SELECT timestamp, open, high, low, close, volume FROM market_candles "
        "WHERE symbol=? AND timeframe=? ORDER BY timestamp",
        (SYMBOL, tf),
    ).fetchall()
    conn.close()
    return rows


def segment_stretches(candles, tf_seconds):
    """Split into continuous stretches."""
    stretches = []
    if not candles:
        return stretches
    expected = tf_seconds
    current = [candles[0]]
    for c in candles[1:]:
        delta = c[0] - current[-1][0]
        if delta <= expected * 1.1:  # 10% tolerance
            current.append(c)
        else:
            stretches.append(current)
            current = [c]
    stretches.append(current)
    return [s for s in stretches if len(s) >= MIN_STRETCH]


def tf_seconds(tf):
    units = {"m": 60, "H": 3600, "D": 86400, "1D": 86400}
    num = int(tf[:-1]) if tf[-1] in "mHD" else 1
    if tf == "1D":
        return 86400
    unit = tf[-1]
    return num * units.get(unit, 60)


def ema(values, period):
    out = [None] * len(values)
    if len(values) < period:
        return out
    k = 2.0 / (period + 1)
    e = sum(values[:period]) / period
    out[period - 1] = e
    for i in range(period, len(values)):
        e = values[i] * k + e * (1 - k)
        out[i] = e
    return out


def rsi(closes, period):
    out = [None] * len(closes)
    if len(closes) < period + 1:
        return out
    gains, losses = [], []
    for i in range(1, period + 1):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    ag = sum(gains) / period
    al = sum(losses) / period
    out[period] = 100.0 if al == 0 else 100 - (100 / (1 + ag / al))
    for i in range(period + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        g = max(d, 0)
        l = max(-d, 0)
        ag = (ag * (period - 1) + g) / period
        al = (al * (period - 1) + l) / period
        out[i] = 100.0 if al == 0 else 100 - (100 / (1 + ag / al))
    return out


def atr(highs, lows, closes, period=14):
    trs = [None] * len(closes)
    for i in range(1, len(closes)):
        h, l, pc = highs[i], lows[i], closes[i - 1]
        trs[i] = max(h - l, abs(h - pc), abs(l - pc))
    out = [None] * len(closes)
    if len([t for t in trs if t is not None]) < period:
        return out
    a = sum(trs[1:period + 1]) / period
    out[period] = a
    for i in range(period + 1, len(closes)):
        a = (a * (period - 1) + trs[i]) / period
        out[i] = a
    return out


def backtest_stretch(stretch, strategy, cfg, fee):
    closes = [c[4] for c in stretch]
    highs = [c[2] for c in stretch]
    lows = [c[3] for c in stretch]
    n = len(closes)

    trades = []
    in_pos = False
    direction = None
    entry = None
    entry_idx = None
    tp_price = None
    sl_price = None

    if strategy == "rsi":
        r_values = rsi(closes, cfg["rsi_period"])
        a_values = atr(highs, lows, closes, 14)
        ef = ema(closes, 50) if cfg["use_trend_filter"] else None
        es = ema(closes, 200) if cfg["use_trend_filter"] else None
        start = max(cfg["rsi_period"] + 1, 15, 200 if cfg["use_trend_filter"] else 15)

        for i in range(start, n):
            price = closes[i]
            if in_pos:
                hold = i - entry_idx
                if direction == "BUY":
                    if price <= sl_price:
                        trades.append((sl_price - entry) / entry - fee)
                        in_pos = False; continue
                    if price >= tp_price:
                        trades.append((tp_price - entry) / entry - fee)
                        in_pos = False; continue
                else:
                    if price >= sl_price:
                        trades.append((entry - sl_price) / entry - fee)
                        in_pos = False; continue
                    if price <= tp_price:
                        trades.append((entry - tp_price) / entry - fee)
                        in_pos = False; continue
                if hold >= cfg["max_hold"]:
                    pnl = (price - entry) / entry if direction == "BUY" else (entry - price) / entry
                    trades.append(pnl - fee)
                    in_pos = False
                continue

            r = r_values[i]; a = a_values[i]
            if r is None or a is None or a <= 0:
                continue
            trend_ok_buy = True
            trend_ok_sell = True
            if cfg["use_trend_filter"]:
                if ef[i] is None or es[i] is None:
                    continue
                trend_ok_buy = ef[i] > es[i]
                trend_ok_sell = ef[i] < es[i]
            if r < cfg["oversold"] and trend_ok_buy:
                in_pos = True; direction = "BUY"; entry = price; entry_idx = i
                tp_price = entry + cfg["atr_tp"] * a
                sl_price = entry - cfg["atr_sl"] * a
            elif r > cfg["overbought"] and trend_ok_sell:
                in_pos = True; direction = "SELL"; entry = price; entry_idx = i
                tp_price = entry - cfg["atr_tp"] * a
                sl_price = entry + cfg["atr_sl"] * a

    elif strategy == "ema_cross":
        ef = ema(closes, cfg["fast"])
        es = ema(closes, cfg["slow"])
        a_values = atr(highs, lows, closes, 14)
        start = max(cfg["slow"] + 1, 15)

        for i in range(start, n):
            price = closes[i]
            if in_pos:
                hold = i - entry_idx
                if direction == "BUY":
                    if price <= sl_price:
                        trades.append((sl_price - entry) / entry - fee)
                        in_pos = False; continue
                    if price >= tp_price:
                        trades.append((tp_price - entry) / entry - fee)
                        in_pos = False; continue
                else:
                    if price >= sl_price:
                        trades.append((entry - sl_price) / entry - fee)
                        in_pos = False; continue
                    if price <= tp_price:
                        trades.append((entry - tp_price) / entry - fee)
                        in_pos = False; continue
                if hold >= cfg["max_hold"]:
                    pnl = (price - entry) / entry if direction == "BUY" else (entry - price) / entry
                    trades.append(pnl - fee)
                    in_pos = False
                continue

            a = a_values[i]
            if ef[i - 1] is None or es[i - 1] is None or ef[i] is None or es[i] is None:
                continue
            if a is None or a <= 0:
                continue
            cross_up = ef[i - 1] <= es[i - 1] and ef[i] > es[i]
            cross_down = ef[i - 1] >= es[i - 1] and ef[i] < es[i]
            if cross_up:
                in_pos = True; direction = "BUY"; entry = price; entry_idx = i
                tp_price = entry + cfg["atr_tp"] * a
                sl_price = entry - cfg["atr_sl"] * a
            elif cross_down:
                in_pos = True; direction = "SELL"; entry = price; entry_idx = i
                tp_price = entry - cfg["atr_tp"] * a
                sl_price = entry + cfg["atr_sl"] * a

    return trades


def summarize(trades):
    if not trades:
        return None
    n = len(trades)
    wins = sum(1 for t in trades if t > 0)
    total = sum(trades)
    return {
        "n": n,
        "wins": wins,
        "wr": wins / n * 100,
        "ev_pct": total / n * 100,
        "total_pct": total * 100,
    }


def main():
    results = []

    for tf in TIMEFRAMES:
        candles = load_candles(tf)
        sec = tf_seconds(tf)
        stretches = segment_stretches(candles, sec)
        usable_cycles = sum(len(s) for s in stretches)
        print(f"[{tf}] total={len(candles)}, stretches={len(stretches)}, "
              f"usable={usable_cycles}")

        if len(stretches) < 3:
            print(f"  -> skip ({tf} has too few stretches)")
            continue

        configs = []

        # RSI configs
        for rp, (os_, ob) in product((7, 14, 21), ((25, 75), (30, 70))):
            for (tp_, sl_) in ((2.0, 1.0), (3.0, 1.5)):
                for hold in (10, 20):
                    for tfilt in (True, False):
                        configs.append(("rsi", {
                            "rsi_period": rp, "oversold": os_, "overbought": ob,
                            "atr_tp": tp_, "atr_sl": sl_,
                            "max_hold": hold, "use_trend_filter": tfilt,
                        }))

        # EMA cross configs
        for fast, slow in product((5, 10, 20), (20, 50, 100)):
            if fast >= slow:
                continue
            for (tp_, sl_) in ((2.0, 1.0), (3.0, 1.5)):
                for hold in (20, 40):
                    configs.append(("ema_cross", {
                        "fast": fast, "slow": slow,
                        "atr_tp": tp_, "atr_sl": sl_,
                        "max_hold": hold,
                    }))

        for fee in FEES:
            for strategy, cfg in configs:
                all_trades = []
                for s in stretches:
                    all_trades.extend(backtest_stretch(s, strategy, cfg, fee))
                summ = summarize(all_trades)
                if summ and summ["n"] >= 10:
                    results.append({
                        "tf": tf, "fee": fee,
                        "strategy": strategy,
                        "cfg": cfg, **summ,
                    })

    results.sort(key=lambda r: r["ev_pct"], reverse=True)

    print()
    print("=" * 130)
    print("TOP 30 CONFIGS (sorted by EV) — all timeframes, both fees")
    print("=" * 130)
    print(f"{'tf':>4} {'fee':>6} {'strat':>10} {'cfg':>40} {'n':>5} "
          f"{'wr':>6} {'ev%':>10} {'tot%':>9}")
    print("-" * 130)

    for r in results[:30]:
        cfg_str = " ".join(f"{k}={v}" for k, v in r["cfg"].items())
        if len(cfg_str) > 40:
            cfg_str = cfg_str[:37] + "..."
        fee_pct = r["fee"] * 100
        print(f"{r['tf']:>4} {fee_pct:>5.2f}% {r['strategy']:>10} "
              f"{cfg_str:>40} {r['n']:>5} {r['wr']:>5.1f}% "
              f"{r['ev_pct']:>+9.4f}% {r['total_pct']:>+8.2f}%")

    positive = [r for r in results if r["ev_pct"] > 0]
    print()
    print("=" * 130)
    print(f"SUMMARY: {len(positive)} / {len(results)} configs have POSITIVE EV")
    print("=" * 130)

    if positive:
        print()
        print(">>> WINNERS:")
        for r in positive[:5]:
            cfg_str = " ".join(f"{k}={v}" for k, v in r["cfg"].items())
            print(f"  [{r['tf']}] fee={r['fee']*100:.2f}% {r['strategy']} "
                  f"{cfg_str}  n={r['n']}  ev={r['ev_pct']:+.4f}%")
    else:
        print()
        print(">>> NO CONFIG has positive EV at any timeframe or fee.")
        print(">>> Simple strategies don't work on this BTC data.")
        print(">>> Need: ML, order flow, or fundamentally different approach.")


if __name__ == "__main__":
    main()