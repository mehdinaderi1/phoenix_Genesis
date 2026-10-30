"""
tools/backtest_adx_breakout.py — Backtest TakeProfit ADX Breakout strategy

Rules (from TakeProfit built-in strategy):
  - ADX period = 14, smoothing = 14
  - If ADX < 18 → market considered in consolidation
  - Box = highest high / lowest low of last 20 candles (during consolidation)
  - Breakout above upper → LONG, below lower → SHORT
  - TP = box_width * 1.0, SL = box_width * 0.5

Usage:
    python tools/backtest_adx_breakout.py
    python tools/backtest_adx_breakout.py --tf 1H
    python tools/backtest_adx_breakout.py --adx-threshold 20
"""
import os, sys, csv, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = "data/historical"

# ═══════════════════════════════════════════════════════════
# CONFIG (TakeProfit defaults)
# ═══════════════════════════════════════════════════════════
ADX_PERIOD        = 14
ADX_SMOOTH        = 14
ADX_THRESHOLD     = 18.0
BOX_LOOKBACK      = 20
TP_MULTIPLE       = 1.0
SL_MULTIPLE       = 0.5
MAX_HOLD_BARS     = 200     # safety exit


# ═══════════════════════════════════════════════════════════
# INDICATORS
# ═══════════════════════════════════════════════════════════
def _wilder_smooth(values, period):
    """Wilder's smoothing (used in ADX). Returns list aligned with input."""
    out = [None] * len(values)
    if len(values) < period:
        return out
    # first value = SMA of first `period`
    first = sum(values[:period]) / period
    out[period - 1] = first
    for i in range(period, len(values)):
        out[i] = (out[i - 1] * (period - 1) + values[i]) / period
    return out


def compute_adx(highs, lows, closes, period=14):
    """Return ADX list (aligned). Wilder's method."""
    n = len(highs)
    if n < period * 2:
        return [None] * n

    tr = [None] * n
    plus_dm = [0.0] * n
    minus_dm = [0.0] * n

    for i in range(1, n):
        h, l, pc = highs[i], lows[i], closes[i - 1]
        tr[i] = max(h - l, abs(h - pc), abs(l - pc))
        up = highs[i] - highs[i - 1]
        down = lows[i - 1] - lows[i]
        plus_dm[i] = up if (up > down and up > 0) else 0.0
        minus_dm[i] = down if (down > up and down > 0) else 0.0

    # smooth TR, +DM, -DM
    tr_s = _wilder_smooth([x if x is not None else 0 for x in tr], period)
    pdm_s = _wilder_smooth(plus_dm, period)
    mdm_s = _wilder_smooth(minus_dm, period)

    plus_di = [None] * n
    minus_di = [None] * n
    dx = [None] * n

    for i in range(n):
        if tr_s[i] and tr_s[i] > 0:
            plus_di[i] = 100 * pdm_s[i] / tr_s[i]
            minus_di[i] = 100 * mdm_s[i] / tr_s[i]
            denom = plus_di[i] + minus_di[i]
            if denom > 0:
                dx[i] = 100 * abs(plus_di[i] - minus_di[i]) / denom

    adx = _wilder_smooth([x if x is not None else 0 for x in dx], period)
    return adx


# ═══════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════
def load_csv(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "ts": int(float(r["timestamp"])),
                "open": float(r["open"]),
                "high": float(r["high"]),
                "low": float(r["low"]),
                "close": float(r["close"]),
                "volume": float(r["volume"]),
            })
    rows.sort(key=lambda x: x["ts"])
    return rows


def find_data_files(tf):
    files = []
    for f in sorted(os.listdir(DATA_DIR)):
        if f.endswith(f"_{tf}.csv") and not f.startswith("BTC"):
            files.append(os.path.join(DATA_DIR, f))
    return files


# ═══════════════════════════════════════════════════════════
# BACKTEST
# ═══════════════════════════════════════════════════════════
def backtest_one(candles, adx_threshold, tp_mult, sl_mult, box_lookback):
    n = len(candles)
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    closes = [c["close"] for c in candles]

    adx = compute_adx(highs, lows, closes, ADX_PERIOD)

    trades = []
    i = max(ADX_PERIOD * 2 + box_lookback, box_lookback + 1)

    while i < n - 1:
        if adx[i] is None or adx[i] >= adx_threshold:
            i += 1
            continue

        # consolidation → build box from last box_lookback candles
        window_hi = max(highs[i - box_lookback:i])
        window_lo = min(lows[i - box_lookback:i])
        box_width = window_hi - window_lo
        if box_width <= 0:
            i += 1
            continue

        # look for breakout on next candles
        entry = None
        side = None
        for j in range(i + 1, min(i + 1 + box_lookback, n)):
            c = candles[j]
            if c["close"] > window_hi:
                side = "LONG"; entry = c["close"]; entry_i = j; break
            if c["close"] < window_lo:
                side = "SHORT"; entry = c["close"]; entry_i = j; break

        if entry is None:
            i += 1
            continue

        if side == "LONG":
            tp = entry + box_width * tp_mult
            sl = entry - box_width * sl_mult
        else:
            tp = entry - box_width * tp_mult
            sl = entry + box_width * sl_mult

        # simulate forward
        outcome = None
        exit_price = None
        exit_i = None
        for k in range(entry_i + 1, min(entry_i + 1 + MAX_HOLD_BARS, n)):
            h, l = candles[k]["high"], candles[k]["low"]
            if side == "LONG":
                if l <= sl:
                    outcome = "LOSS"; exit_price = sl; exit_i = k; break
                if h >= tp:
                    outcome = "WIN"; exit_price = tp; exit_i = k; break
            else:
                if h >= sl:
                    outcome = "LOSS"; exit_price = sl; exit_i = k; break
                if l <= tp:
                    outcome = "WIN"; exit_price = tp; exit_i = k; break

        if outcome is None:
            outcome = "OPEN"
            exit_i = min(entry_i + MAX_HOLD_BARS, n - 1)
            exit_price = closes[exit_i]

        risk = abs(entry - sl)
        if risk <= 0:
            i = entry_i + 1
            continue
        r_mult = (exit_price - entry) / risk if side == "LONG" else (entry - exit_price) / risk

        trades.append({
            "side": side, "entry_ts": candles[entry_i]["ts"],
            "entry": entry, "sl": sl, "tp": tp,
            "exit_ts": candles[exit_i]["ts"], "exit_price": exit_price,
            "outcome": outcome, "r": r_mult,
        })

        # after trade closes, skip ahead
        i = exit_i + 1

    return trades


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════
def summarize(trades, label):
    if not trades:
        return {"label": label, "n": 0}
    wins = [t for t in trades if t["outcome"] == "WIN"]
    losses = [t for t in trades if t["outcome"] == "LOSS"]
    opens = [t for t in trades if t["outcome"] == "OPEN"]
    total_r = sum(t["r"] for t in trades)
    win_r = sum(t["r"] for t in wins)
    loss_r = sum(t["r"] for t in losses)
    pf = (win_r / abs(loss_r)) if loss_r < 0 else (float("inf") if win_r > 0 else 0)
    wr = len(wins) / (len(wins) + len(losses)) * 100 if (wins or losses) else 0
    return {
        "label": label, "n": len(trades),
        "wins": len(wins), "losses": len(losses), "opens": len(opens),
        "wr": wr, "total_r": total_r,
        "avg_r": total_r / len(trades),
        "avg_win": win_r / len(wins) if wins else 0,
        "avg_loss": loss_r / len(losses) if losses else 0,
        "pf": pf,
    }


def print_stats(s):
    if s["n"] == 0:
        print(f"\n[{s['label']}] no trades"); return
    print(f"\n[{s['label']}]")
    print(f"  trades:        {s['n']}")
    print(f"  W/L/OPEN:      {s['wins']}/{s['losses']}/{s['opens']}")
    print(f"  win rate:      {s['wr']:.1f}%")
    print(f"  total R:       {s['total_r']:+.2f}")
    print(f"  avg R/trade:   {s['avg_r']:+.3f}")
    print(f"  avg win:       {s['avg_win']:+.2f} R")
    print(f"  avg loss:      {s['avg_loss']:+.2f} R")
    print(f"  profit factor: {s['pf']:.2f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tf", default="1H", choices=["1H", "4H"])
    ap.add_argument("--adx-threshold", type=float, default=ADX_THRESHOLD)
    ap.add_argument("--tp-mult", type=float, default=TP_MULTIPLE)
    ap.add_argument("--sl-mult", type=float, default=SL_MULTIPLE)
    ap.add_argument("--box-lookback", type=int, default=BOX_LOOKBACK)
    args = ap.parse_args()

    files = find_data_files(args.tf)
    if not files:
        print(f"ERROR: no *_ {args.tf}.csv in {DATA_DIR}"); sys.exit(1)

    print(f"[ADX-BT] TF={args.tf}  ADX<{args.adx_threshold}  box={args.box_lookback}  "
          f"TP={args.tp_mult}×box  SL={args.sl_mult}×box")
    print(f"[ADX-BT] {len(files)} symbols\n")

    all_trades = []
    per_symbol = {}
    for path in files:
        sym = os.path.basename(path).rsplit("_", 1)[0]
        candles = load_csv(path)
        trades = backtest_one(candles, args.adx_threshold, args.tp_mult, args.sl_mult, args.box_lookback)
        per_symbol[sym] = trades
        all_trades.extend(trades)
        print(f"[BT] {sym:10s} setups: {len(trades):3d}")

    print("\n" + "=" * 70)
    print("ADX BREAKOUT — BACKTEST SUMMARY")
    print("=" * 70)

    print_stats(summarize(all_trades, "ALL"))
    print_stats(summarize([t for t in all_trades if t["side"] == "LONG"], "LONG only"))
    print_stats(summarize([t for t in all_trades if t["side"] == "SHORT"], "SHORT only"))

    print("\n" + "-" * 70)
    print("Per symbol:")
    print(f"  {'SYMBOL':10s} {'N':>4s} {'W/L':>7s} {'WR%':>6s} {'TotR':>7s} {'AvgR':>7s}")
    for sym, trades in sorted(per_symbol.items(), key=lambda kv: -len(kv[1])):
        if not trades: continue
        s = summarize(trades, sym)
        print(f"  {sym:10s} {s['n']:>4d} {s['wins']:>3d}/{s['losses']:<3d} "
              f"{s['wr']:>6.1f} {s['total_r']:>+7.2f} {s['avg_r']:>+7.3f}")


if __name__ == "__main__":
    main()