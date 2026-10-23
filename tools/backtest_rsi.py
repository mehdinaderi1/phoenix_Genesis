"""
RSI Mean-Reversion Backtest on 5m candles.
"""
import json
import sqlite3
from pathlib import Path

FEE_PCT = 0.0012


def find_candle_data():
    candidates = list(Path("data").glob("*.db")) + list(Path("data").glob("**/*.db"))
    for db_path in candidates:
        try:
            conn = sqlite3.connect(str(db_path))
            cur = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='market_candles'"
            )
            if not cur.fetchone():
                conn.close()
                continue
            cur = conn.execute(
                "SELECT timeframe, COUNT(*) FROM market_candles WHERE symbol='BTCUSDT' "
                "GROUP BY timeframe"
            )
            rows = cur.fetchall()
            conn.close()
            if rows:
                return db_path, dict(rows)
        except Exception:
            continue
    return None, {}


def load_5m_candles(db_path):
    conn = sqlite3.connect(str(db_path))
    cur = conn.execute(
        "SELECT timestamp, open, high, low, close, volume FROM market_candles "
        "WHERE symbol='BTCUSDT' AND timeframe='5m' ORDER BY timestamp"
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def compute_ema(values, period):
    emas = [None] * len(values)
    if len(values) < period:
        return emas
    k = 2.0 / (period + 1)
    ema = sum(values[:period]) / period
    emas[period - 1] = ema
    for i in range(period, len(values)):
        ema = values[i] * k + ema * (1 - k)
        emas[i] = ema
    return emas


def compute_rsi(closes, period=14):
    rsis = [None] * len(closes)
    if len(closes) < period + 1:
        return rsis
    gains, losses = [], []
    for i in range(1, period + 1):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    rsis[period] = 100.0 if avg_loss == 0 else 100 - (100 / (1 + avg_gain / avg_loss))
    for i in range(period + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        gain = max(d, 0)
        loss = max(-d, 0)
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        rsis[i] = 100.0 if avg_loss == 0 else 100 - (100 / (1 + avg_gain / avg_loss))
    return rsis


def compute_atr(highs, lows, closes, period=14):
    trs = [None] * len(closes)
    for i in range(1, len(closes)):
        h, l, pc = highs[i], lows[i], closes[i - 1]
        trs[i] = max(h - l, abs(h - pc), abs(l - pc))
    atrs = [None] * len(closes)
    if len([x for x in trs if x is not None]) < period:
        return atrs
    atr = sum(trs[1:period + 1]) / period
    atrs[period] = atr
    for i in range(period + 1, len(closes)):
        atr = (atr * (period - 1) + trs[i]) / period
        atrs[i] = atr
    return atrs


def backtest_config(candles, rsi_period, oversold, overbought,
                    atr_tp_mult, atr_sl_mult, max_hold, use_trend_filter):
    closes = [c[4] for c in candles]
    highs = [c[2] for c in candles]
    lows = [c[3] for c in candles]

    rsis = compute_rsi(closes, rsi_period)
    atrs = compute_atr(highs, lows, closes, 14)
    ema_fast = compute_ema(closes, 50)
    ema_slow = compute_ema(closes, 200)

    trades = []
    in_pos = False
    direction = None
    entry_price = None
    entry_idx = None
    tp_price = None
    sl_price = None

    start = max(rsi_period + 1, 14 + 1, 200)

    for i in range(start, len(candles)):
        price = closes[i]

        if in_pos:
            hold = i - entry_idx
            if direction == "BUY":
                if price <= sl_price:
                    trades.append({"result": "SL", "pnl_pct": (sl_price - entry_price) / entry_price - FEE_PCT, "hold": hold})
                    in_pos = False
                    continue
                if price >= tp_price:
                    trades.append({"result": "TP", "pnl_pct": (tp_price - entry_price) / entry_price - FEE_PCT, "hold": hold})
                    in_pos = False
                    continue
            else:
                if price >= sl_price:
                    trades.append({"result": "SL", "pnl_pct": (entry_price - sl_price) / entry_price - FEE_PCT, "hold": hold})
                    in_pos = False
                    continue
                if price <= tp_price:
                    trades.append({"result": "TP", "pnl_pct": (entry_price - tp_price) / entry_price - FEE_PCT, "hold": hold})
                    in_pos = False
                    continue
            if hold >= max_hold:
                pnl = (price - entry_price) / entry_price if direction == "BUY" else (entry_price - price) / entry_price
                trades.append({"result": "TIMEOUT", "pnl_pct": pnl - FEE_PCT, "hold": hold})
                in_pos = False
            continue

        r = rsis[i]
        a = atrs[i]
        if r is None or a is None or a <= 0:
            continue

        trend_ok_buy = True
        trend_ok_sell = True
        if use_trend_filter:
            ef, es = ema_fast[i], ema_slow[i]
            if ef is None or es is None:
                continue
            trend_ok_buy = ef > es
            trend_ok_sell = ef < es

        if r < oversold and trend_ok_buy:
            in_pos = True
            direction = "BUY"
            entry_price = price
            entry_idx = i
            tp_price = entry_price + atr_tp_mult * a
            sl_price = entry_price - atr_sl_mult * a
        elif r > overbought and trend_ok_sell:
            in_pos = True
            direction = "SELL"
            entry_price = price
            entry_idx = i
            tp_price = entry_price - atr_tp_mult * a
            sl_price = entry_price + atr_sl_mult * a

    if in_pos:
        price = closes[-1]
        pnl = (price - entry_price) / entry_price if direction == "BUY" else (entry_price - price) / entry_price
        trades.append({"result": "OPEN", "pnl_pct": pnl - FEE_PCT, "hold": len(candles) - entry_idx})

    return trades


def summarize(trades):
    n = len(trades)
    if n == 0:
        return None
    wins = sum(1 for t in trades if t["pnl_pct"] > 0)
    total = sum(t["pnl_pct"] for t in trades)
    return {
        "n": n,
        "wins": wins,
        "win_rate": wins / n * 100,
        "ev_pct": total / n * 100,
        "total_pct": total * 100,
        "avg_hold": sum(t["hold"] for t in trades) / n,
    }


def main():
    db, tables = find_candle_data()
    if not db:
        print("No DB with market_candles found.")
        return

    print(f"DB: {db}")
    print(f"Timeframes available: {tables}")
    print()

    if "5m" not in tables or tables["5m"] < 300:
        print(f"Insufficient 5m candles: {tables.get('5m', 0)}. Need >= 300.")
        return

    candles = load_5m_candles(db)
    print(f"Loaded {len(candles)} candles of 5m BTCUSDT")
    print(f"  from {candles[0][0]} to {candles[-1][0]}")
    span_hours = (candles[-1][0] - candles[0][0]) / 3600.0
    print(f"  span: {span_hours:.1f} hours (~{span_hours/24:.1f} days)")
    print()

    configs = []
    for rsi_period in (7, 14, 21):
        for oversold, overbought in ((25, 75), (30, 70), (35, 65)):
            for atr_tp, atr_sl in ((1.5, 1.0), (2.0, 1.0), (2.0, 1.5), (3.0, 1.5)):
                for max_hold in (10, 20, 40):
                    for trend_filter in (False, True):
                        configs.append({
                            "rsi_period": rsi_period,
                            "oversold": oversold,
                            "overbought": overbought,
                            "atr_tp_mult": atr_tp,
                            "atr_sl_mult": atr_sl,
                            "max_hold": max_hold,
                            "use_trend_filter": trend_filter,
                        })

    print(f"Testing {len(configs)} configurations...")
    print()

    results = []
    for cfg in configs:
        trades = backtest_config(candles, **cfg)
        summ = summarize(trades)
        if summ and summ["n"] >= 5:
            results.append((cfg, summ))

    results.sort(key=lambda x: x[1]["ev_pct"], reverse=True)

    print(f"{'rsi':>4} {'os/ob':>7} {'tp/sl':>8} {'hold':>5} {'tf':>5} "
          f"{'n':>4} {'wr%':>6} {'ev%':>10} {'tot%':>8} {'avgHold':>8}")
    print("-" * 78)
    for cfg, s in results[:20]:
        print(
            f"{cfg['rsi_period']:>4} "
            f"{cfg['oversold']:>2}/{cfg['overbought']:<4} "
            f"{cfg['atr_tp_mult']:.1f}/{cfg['atr_sl_mult']:.1f} "
            f"{cfg['max_hold']:>5} "
            f"{'yes' if cfg['use_trend_filter'] else 'no':>5} "
            f"{s['n']:>4} {s['win_rate']:>5.1f}% "
            f"{s['ev_pct']:>+9.4f}% {s['total_pct']:>+7.2f}% "
            f"{s['avg_hold']:>8.1f}"
        )

    if not results:
        print("No config produced >= 5 trades.")
        print("Try relaxing oversold/overbought or increasing data.")
        return

    best_cfg, best_s = results[0]
    print()
    print("=" * 78)
    print("BEST CONFIG")
    print("=" * 78)
    print(json.dumps(best_cfg, indent=2))
    print(f"Trades: {best_s['n']}")
    print(f"Win rate: {best_s['win_rate']:.1f}%")
    print(f"EV/trade: {best_s['ev_pct']:+.4f}%")
    print(f"Total: {best_s['total_pct']:+.2f}%")
    print()
    if best_s["ev_pct"] > 0:
        print(f">>> POSITIVE EDGE FOUND: {best_s['ev_pct']:+.4f}% per trade")
    else:
        print(">>> Still negative. Try different strategy or more data.")


if __name__ == "__main__":
    main()