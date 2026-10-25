"""
strategy_lab.py — 5m backtest lab for Phoenix Genesis

Strategy: Double Bottom + RSI Divergence + ATR-based SL/TP + time exit

Metrics: EV, win rate, profit factor, per-trade Sharpe, max DD
Safety:  Drift Control (random baseline) + Walk-forward split

Usage:
    python tools/strategy_lab.py
    python tools/strategy_lab.py --tf 5m --fee 0.0004
"""
import argparse
import json
import random
import sqlite3
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Tuple


# ─────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────

@dataclass
class Candle:
    ts: int
    o: float
    h: float
    l: float
    c: float
    v: float


def load_candles(db_path: str, symbol: str = "BTCUSDT", timeframe: str = "5m") -> List[Candle]:
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT timestamp, open, high, low, close, volume "
        "FROM market_candles WHERE symbol=? AND timeframe=? ORDER BY timestamp",
        (symbol, timeframe),
    ).fetchall()
    conn.close()
    return [Candle(r[0], r[1], r[2], r[3], r[4], r[5] or 0) for r in rows]


def segment_stretches(candles: List[Candle], tf_seconds: int, min_len: int = 250) -> List[List[Candle]]:
    if not candles:
        return []
    stretches = []
    current = [candles[0]]
    for c in candles[1:]:
        if c.ts - current[-1].ts <= tf_seconds * 1.1:
            current.append(c)
        else:
            if len(current) >= min_len:
                stretches.append(current)
            current = [c]
    if len(current) >= min_len:
        stretches.append(current)
    return stretches


# ─────────────────────────────────────────────────────────────
# INDICATORS (pure Python, Wilder's smoothing)
# ─────────────────────────────────────────────────────────────

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


def rsi(closes, period=14):
    out = [None] * len(closes)
    if len(closes) < period + 1:
        return out
    gains, losses = [], []
    for i in range(1, period + 1):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0.0))
        losses.append(max(-d, 0.0))
    ag = sum(gains) / period
    al = sum(losses) / period
    out[period] = 100.0 if al == 0 else 100 - (100 / (1 + ag / al))
    for i in range(period + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        g = max(d, 0.0)
        l = max(-d, 0.0)
        ag = (ag * (period - 1) + g) / period
        al = (al * (period - 1) + l) / period
        out[i] = 100.0 if al == 0 else 100 - (100 / (1 + ag / al))
    return out


def atr(highs, lows, closes, period=14):
    trs = [None] * len(closes)
    for i in range(1, len(closes)):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        trs[i] = tr
    out = [None] * len(closes)
    if len([t for t in trs if t is not None]) < period:
        return out
    a = sum(trs[1:period + 1]) / period
    out[period] = a
    for i in range(period + 1, len(closes)):
        a = (a * (period - 1) + trs[i]) / period
        out[i] = a
    return out


# ─────────────────────────────────────────────────────────────
# STRATEGY: Double Bottom + RSI Divergence + ATR
# ─────────────────────────────────────────────────────────────

@dataclass
class StrategyParams:
    pivot_lookback: int = 3
    min_bars_between: int = 10
    tolerance_pct: float = 0.005      # 0.5%
    rsi_period: int = 14
    atr_period: int = 14
    sl_atr_mult: float = 1.0
    rr_ratio: float = 2.0
    time_exit_bars: int = 48           # 4 hours on 5m
    warmup_bars: int = 250


def find_confirmed_low_pivots(lows: List[float], lookback: int) -> List[Tuple[int, int, float]]:
    """Returns (pivot_idx, confirmed_at_idx, price)."""
    pivots = []
    for i in range(lookback, len(lows) - lookback):
        is_low = True
        for j in range(1, lookback + 1):
            if lows[i] >= lows[i - j] or lows[i] >= lows[i + j]:
                is_low = False
                break
        if is_low:
            pivots.append((i, i + lookback, lows[i]))
    return pivots


def generate_signals(candles: List[Candle], p: StrategyParams) -> List[dict]:
    n = len(candles)
    if n < p.warmup_bars:
        return []

    closes = [c.c for c in candles]
    highs = [c.h for c in candles]
    lows = [c.l for c in candles]

    rsi_vals = rsi(closes, p.rsi_period)
    atr_vals = atr(highs, lows, closes, p.atr_period)
    pivot_lows = find_confirmed_low_pivots(lows, p.pivot_lookback)

    # Pre-index pivots by confirmation index for fast lookup
    pivots_by_conf = sorted(pivot_lows, key=lambda x: x[1])

    signals = []
    for i in range(p.warmup_bars, n):
        # Get pivots confirmed by now
        confirmed = [(p_idx, price) for p_idx, conf, price in pivots_by_conf if conf <= i]
        if len(confirmed) < 2:
            continue

        p2_idx, low2 = confirmed[-1]
        p1_idx, low1 = confirmed[-2]

        if p2_idx - p1_idx < p.min_bars_between:
            continue
        if low1 <= 0:
            continue
        if abs(low1 - low2) / low1 > p.tolerance_pct:
            continue

        if rsi_vals[p1_idx] is None or rsi_vals[p2_idx] is None:
            continue
        if rsi_vals[p2_idx] <= rsi_vals[p1_idx]:
            continue  # no bullish divergence

        neckline = max(highs[p1_idx:p2_idx + 1])

        # Entry trigger: close above neckline, previous bar below
        if i == 0:
            continue
        if not (closes[i] > neckline and closes[i - 1] <= neckline):
            continue

        if atr_vals[i] is None or atr_vals[i] <= 0:
            continue

        entry = closes[i]
        sl = low2 - p.sl_atr_mult * atr_vals[i]
        risk = entry - sl
        if risk <= 0:
            continue
        tp = entry + p.rr_ratio * risk

        signals.append({
            "entry_idx": i,
            "entry_price": entry,
            "sl": sl,
            "tp": tp,
            "time_exit_idx": min(i + p.time_exit_bars, n - 1),
            "pattern": {
                "p1": p1_idx, "p2": p2_idx,
                "low1": low1, "low2": low2,
                "neckline": neckline,
                "rsi1": rsi_vals[p1_idx],
                "rsi2": rsi_vals[p2_idx],
            },
        })

    return signals


# ─────────────────────────────────────────────────────────────
# SIMULATION
# ─────────────────────────────────────────────────────────────

def simulate_signals(signals: List[dict], candles: List[Candle], fee_pct: float) -> List[dict]:
    trades = []
    for sig in signals:
        entry_idx = sig["entry_idx"]
        entry_price = sig["entry_price"]
        sl = sig["sl"]
        tp = sig["tp"]
        time_exit = sig["time_exit_idx"]

        exit_idx, exit_price, reason = None, None, None
        for j in range(entry_idx + 1, min(time_exit + 1, len(candles))):
            c = candles[j]
            # Conservative: SL hit intrabar before TP
            if c.l <= sl:
                exit_idx, exit_price, reason = j, sl, "SL"
                break
            if c.h >= tp:
                exit_idx, exit_price, reason = j, tp, "TP"
                break

        if exit_idx is None:
            exit_idx = min(time_exit, len(candles) - 1)
            exit_price = candles[exit_idx].c
            reason = "TIMEOUT"

        pnl_pct = (exit_price - entry_price) / entry_price - fee_pct
        trades.append({
            "entry_idx": entry_idx,
            "exit_idx": exit_idx,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "pnl_pct": pnl_pct,
            "reason": reason,
            "bars_held": exit_idx - entry_idx,
            "sl": sl, "tp": tp,
        })
    return trades


def simulate_random_entries(candles, n_signals, sl_pct, tp_pct, hold_bars, fee_pct):
    """Random entries with same SL/TP/hold structure."""
    if n_signals <= 0 or len(candles) < hold_bars + 300:
        return []
    max_start = len(candles) - hold_bars - 1
    if max_start <= 300:
        return []
    trades = []
    for _ in range(n_signals):
        entry_idx = random.randint(300, max_start)
        entry_price = candles[entry_idx].c
        sl = entry_price * (1 - sl_pct)
        tp = entry_price * (1 + tp_pct)
        time_exit = entry_idx + hold_bars
        exit_price, reason = candles[min(time_exit, len(candles) - 1)].c, "TIMEOUT"
        for j in range(entry_idx + 1, min(time_exit + 1, len(candles))):
            c = candles[j]
            if c.l <= sl:
                exit_price, reason = sl, "SL"
                break
            if c.h >= tp:
                exit_price, reason = tp, "TP"
                break
        pnl_pct = (exit_price - entry_price) / entry_price - fee_pct
        trades.append({"pnl_pct": pnl_pct, "reason": reason})
    return trades


# ─────────────────────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────────────────────

def compute_metrics(trades: List[dict]) -> dict:
    n = len(trades)
    if n == 0:
        return {"n": 0, "ev_pct": 0.0, "win_rate": 0.0, "profit_factor": 0.0,
                "sharpe_per_trade": 0.0, "max_dd_pct": 0.0, "total_pct": 0.0}

    pnls = [t["pnl_pct"] for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    total = sum(pnls)
    ev = total / n
    win_rate = len(wins) / n

    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    pf = (gross_win / gross_loss) if gross_loss > 0 else (float("inf") if gross_win > 0 else 0.0)

    if n > 1:
        mean = total / n
        var = sum((p - mean) ** 2 for p in pnls) / (n - 1)
        std = var ** 0.5
        sharpe = (mean / std) if std > 0 else 0.0
    else:
        sharpe = 0.0

    equity, peak, max_dd = 0.0, 0.0, 0.0
    for p in pnls:
        equity += p
        if equity > peak:
            peak = equity
        dd = peak - equity
        if dd > max_dd:
            max_dd = dd

    return {
        "n": n,
        "ev_pct": ev * 100,
        "win_rate": win_rate * 100,
        "profit_factor": pf,
        "sharpe_per_trade": sharpe,
        "max_dd_pct": max_dd * 100,
        "total_pct": total * 100,
        "avg_bars": sum(t.get("bars_held", 0) for t in trades) / n if trades and "bars_held" in trades[0] else 0.0,
    }


def drift_control(candles, n_signals, sl_pct, tp_pct, hold_bars, fee_pct, iterations=100):
    evs = []
    for _ in range(iterations):
        trades = simulate_random_entries(candles, n_signals, sl_pct, tp_pct, hold_bars, fee_pct)
        m = compute_metrics(trades)
        evs.append(m["ev_pct"])
    if not evs:
        return {"mean_ev": 0.0, "std_ev": 0.0, "iterations": 0}
    mean = sum(evs) / len(evs)
    std = statistics.pstdev(evs) if len(evs) > 1 else 0.0
    return {"mean_ev": mean, "std_ev": std, "iterations": len(evs)}


# ─────────────────────────────────────────────────────────────
# WALK-FORWARD
# ─────────────────────────────────────────────────────────────

def walk_forward(stretches: List[List[Candle]], params: StrategyParams, fee_pct: float, train_frac=0.7):
    results = {"train": [], "test": []}
    for st in stretches:
        split = int(len(st) * train_frac)
        if split < params.warmup_bars + 100:
            continue
        train_candles = st[:split]
        test_candles = st[split:]

        tr_sig = generate_signals(train_candles, params)
        tr_trades = simulate_signals(tr_sig, train_candles, fee_pct)
        if tr_trades:
            results["train"].extend(tr_trades)

        te_sig = generate_signals(test_candles, params)
        te_trades = simulate_signals(te_sig, test_candles, fee_pct)
        if te_trades:
            results["test"].extend(te_trades)

    return {
        "train_metrics": compute_metrics(results["train"]),
        "test_metrics": compute_metrics(results["test"]),
        "train_n": len(results["train"]),
        "test_n": len(results["test"]),
    }


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="data/phoenix.db")
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--tf", default="5m")
    parser.add_argument("--fee", type=float, default=0.0012, help="round trip (0.0012=taker, 0.0004=maker)")
    parser.add_argument("--drift-iter", type=int, default=100)
    args = parser.parse_args()

    tf_seconds = {"5m": 300, "15m": 900, "30m": 1800, "4H": 14400, "1D": 86400}[args.tf]
    fee_pct = args.fee

    print("=" * 78)
    print(f"STRATEGY LAB — {args.symbol} {args.tf} — fee={fee_pct*100:.2f}% round-trip")
    print("=" * 78)

    candles = load_candles(args.db, args.symbol, args.tf)
    print(f"Loaded {len(candles)} candles")
    if len(candles) < 500:
        print("Not enough data.")
        return

    stretches = segment_stretches(candles, tf_seconds, min_len=250)
    total_usable = sum(len(s) for s in stretches)
    print(f"Continuous stretches: {len(stretches)}, usable candles: {total_usable}")
    print()

    params = StrategyParams()
    all_signals, all_trades = [], []

    for st in stretches:
        sig = generate_signals(st, params)
        tr = simulate_signals(sig, st, fee_pct)
        all_signals.extend(sig)
        all_trades.extend(tr)

    print(f"{'='*78}")
    print("STRATEGY RESULT (full data)")
    print(f"{'='*78}")
    m = compute_metrics(all_trades)
    print(f"  signals:        {len(all_signals)}")
    print(f"  trades:         {m['n']}")
    print(f"  win rate:       {m['win_rate']:.1f}%")
    print(f"  EV/trade:       {m['ev_pct']:+.4f}%")
    print(f"  profit factor:  {m['profit_factor']:.2f}")
    print(f"  Sharpe/trade:   {m['sharpe_per_trade']:+.3f}")
    print(f"  max drawdown:   {m['max_dd_pct']:.2f}%")
    print(f"  total return:   {m['total_pct']:+.2f}%")
    if m["n"] > 0:
        print(f"  avg bars held:  {m.get('avg_bars', 0):.1f}")
    print()

    if m["n"] < 5:
        print("Too few trades to draw conclusions.")
        return

    # ─── Drift Control ───
    if all_signals:
        avg_risk = sum(s["entry_price"] - s["sl"] for s in all_signals) / len(all_signals)
        avg_reward = sum(s["tp"] - s["entry_price"] for s in all_signals) / len(all_signals)
        avg_entry = sum(s["entry_price"] for s in all_signals) / len(all_signals)
        avg_bars = sum(s["time_exit_idx"] - s["entry_idx"] for s in all_signals) / len(all_signals)
        sl_pct = avg_risk / avg_entry
        tp_pct = avg_reward / avg_entry

        print(f"{'='*78}")
        print(f"DRIFT CONTROL (same SL/TP/hold, {args.drift_iter} iterations)")
        print(f"{'='*78}")
        dc = drift_control(
            candles, len(all_signals), sl_pct, tp_pct, int(avg_bars), fee_pct,
            iterations=args.drift_iter,
        )
        print(f"  Random mean EV: {dc['mean_ev']:+.4f}%")
        print(f"  Random std EV:  {dc['std_ev']:.4f}%")
        diff = m["ev_pct"] - dc["mean_ev"]
        z = diff / dc["std_ev"] if dc["std_ev"] > 0 else 0.0
        print(f"  Strategy diff:  {diff:+.4f}%")
        print(f"  Z-score:        {z:+.2f}")
        if z >= 2.0:
            print(f"  >>> SIGNIFICANT: {z:.1f} sigma above random. Edge is real.")
        elif z >= 1.0:
            print(f"  >>> WEAK EDGE: {z:.1f} sigma above random. Needs more data.")
        else:
            print(f"  >>> NO EDGE: within noise of random entries.")
        print()

    # ─── Walk-forward ───
    print(f"{'='*78}")
    print("WALK-FORWARD (70% train / 30% test)")
    print(f"{'='*78}")
    wf = walk_forward(stretches, params, fee_pct, train_frac=0.7)
    print(f"  Train: n={wf['train_n']}, EV={wf['train_metrics']['ev_pct']:+.4f}%, "
          f"WR={wf['train_metrics']['win_rate']:.1f}%, PF={wf['train_metrics']['profit_factor']:.2f}")
    print(f"  Test:  n={wf['test_n']}, EV={wf['test_metrics']['ev_pct']:+.4f}%, "
          f"WR={wf['test_metrics']['win_rate']:.1f}%, PF={wf['test_metrics']['profit_factor']:.2f}")
    if wf["train_n"] > 0 and wf["test_n"] > 0:
        ratio = wf["test_metrics"]["ev_pct"] / wf["train_metrics"]["ev_pct"] if wf["train_metrics"]["ev_pct"] != 0 else 0
        print(f"  Test/Train EV ratio: {ratio:+.2f}")
        if ratio >= 0.5:
            print(f"  >>> OOS survives. Likely not overfit.")
        else:
            print(f"  >>> OOS degrades. Likely overfit.")
    print()

    # ─── Save results ───
    out = {
        "config": vars(args),
        "stretches": len(stretches),
        "metrics": m,
        "drift": dc if all_signals else None,
        "walk_forward": wf,
    }
    Path("data/strategy_lab_results.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8"
    )
    print(f"Results saved to data/strategy_lab_results.json")


if __name__ == "__main__":
    main()