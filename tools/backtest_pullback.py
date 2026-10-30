"""
tools/backtest_pullback.py — Backtest the pullback strategy currently used by Runner

Mirrors the exact logic in futures_strategy_runner._detect:
  - 4H Donchian channel (CHANNEL_PERIOD=30)
  - BTC direction filter from 4H
  - Pullback: pos_pct <= 25 (LONG) / >= 75 (SHORT)
  - Candle confirmation: wick >= 30% + volume >= 1.2x
  - SL at channel edge + buffer, TP at channel mid
  - Hard SL = 5% from initial entry
  - Optional averaging (disabled by default; flag to enable)

Usage:
    python tools/backtest_pullback.py
    python tools/backtest_pullback.py --tf 4H
    python tools/backtest_pullback.py --with-avg
"""
import os, sys, csv, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.futures_strategy_runner import (
    SYMBOLS, TIMEFRAME, CHANNEL_PERIOD, MIN_WIDTH_PCT, MAX_WIDTH_PCT,
    LONG_MAX_POS, SHORT_MIN_POS, SL_BUFFER_PCT,
    HARD_SL_PCT, AVG_ENABLED, AVG_LEVELS_PCT, AVG_SIZE_MULT,
    compute_channel, btc_direction, candle_sig_with_volume,
    _close, _high, _low,
)

DATA_DIR = "data/historical"
MAX_HOLD_BARS = 400  # up to ~66 days on 4H
COMMISSION_PCT = float(os.environ.get("PB_COMMISSION_PCT", "0.05"))  # 0.05% per side = 0.1% round-trip (futures XT)
TRAILING_ENABLED = False
TRAILING_START_PCT = 1.0
TRAILING_DISTANCE_PCT = 0.5

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


def find_4h_idx(candles_4h, ts_4h):
    """Binary search: last index with ts <= ts_4h."""
    lo, hi, ans = 0, len(candles_4h) - 1, -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if candles_4h[mid]["ts"] <= ts_4h:
            ans = mid; lo = mid + 1
        else:
            hi = mid - 1
    return ans


def backtest_symbol(sym, c4h, btc4h, with_avg=False):
    """Walk-forward pullback backtest on 4H candles."""
    n = len(c4h)
    results = []
    start = max(CHANNEL_PERIOD + 20, 60)

    for i in range(start, n - 1):
        ts = c4h[i]["ts"]

        idx_btc = find_4h_idx(btc4h, ts)
        if idx_btc < 60:
            continue
        btc_dir = btc_direction(btc4h[:idx_btc])
        if btc_dir == "UNKNOWN":
            continue

        ch = compute_channel(c4h[:i], CHANNEL_PERIOD)
        if not ch:
            continue
        if ch["width_pct"] < MIN_WIDTH_PCT or ch["width_pct"] > MAX_WIDTH_PCT:
            continue

        price = c4h[i - 1]["close"]
        rng = ch["upper"] - ch["lower"]
        if rng <= 0:
            continue
        pos_pct = (price - ch["lower"]) / rng * 100

        window = c4h[max(0, i - 15):i]
        sig = candle_sig_with_volume(window, window=10)
        if not sig:
            continue

        side = None
        if btc_dir == "UP" and pos_pct <= LONG_MAX_POS and sig["lower_wick_pct"] >= 30 and sig.get("volume_confirmed", False):
            side = "LONG"
        elif btc_dir == "DOWN" and pos_pct >= SHORT_MIN_POS and sig["upper_wick_pct"] >= 30 and sig.get("volume_confirmed", False):
            side = "SHORT"
        elif btc_dir == "FLAT":
            if pos_pct <= LONG_MAX_POS and sig["lower_wick_pct"] >= 30 and sig.get("volume_confirmed", False):
                side = "LONG"
            elif pos_pct >= SHORT_MIN_POS and sig["upper_wick_pct"] >= 30 and sig.get("volume_confirmed", False):
                side = "SHORT"

        if side is None:
            continue

        entry_i = i
        if entry_i >= n - 1:
            break
        entry = c4h[entry_i]["open"]
        initial_entry = entry
        size = 1.0

        if side == "SHORT":
            sl = ch["upper"] * (1 + SL_BUFFER_PCT / 100)
            tp = ch["mid"]
            hard_sl = initial_entry * (1 + HARD_SL_PCT / 100)
        else:
            sl = ch["lower"] * (1 - SL_BUFFER_PCT / 100)
            tp = ch["mid"]
            hard_sl = initial_entry * (1 - HARD_SL_PCT / 100)

        # ─── State init ───
        avg_count = 0
        avg_entries = []
        cur_size = size
        cur_entry = initial_entry
        outcome = None
        exit_price = None
        exit_i = None
        trailing_sl = float("inf") if side == "SHORT" else 0.0

        # ─── Simulation loop ───
        for k in range(entry_i + 1, min(entry_i + 1 + MAX_HOLD_BARS, n)):
            c = c4h[k]
            hi, lo = c["high"], c["low"]
            cur_close = c["close"]

            # 1) Exits (with current candle's hi/lo)
            if side == "SHORT" and hi >= hard_sl:
                outcome, exit_price, exit_i = "HARD_SL", hard_sl, k; break
            if side == "LONG" and lo <= hard_sl:
                outcome, exit_price, exit_i = "HARD_SL", hard_sl, k; break

            if TRAILING_ENABLED:
                if side == "LONG" and trailing_sl > 0 and lo <= trailing_sl:
                    outcome, exit_price, exit_i = "TRAIL_SL", trailing_sl, k; break
                if side == "SHORT" and trailing_sl < float("inf") and hi >= trailing_sl:
                    outcome, exit_price, exit_i = "TRAIL_SL", trailing_sl, k; break

            if side == "SHORT" and lo <= tp:
                outcome, exit_price, exit_i = "TP", tp, k; break
            if side == "LONG" and hi >= tp:
                outcome, exit_price, exit_i = "TP", tp, k; break

            # 2) Trailing update — affects NEXT candle only
            if TRAILING_ENABLED:
                if side == "LONG":
                    if cur_close >= initial_entry * (1 + TRAILING_START_PCT / 100):
                        new_sl = cur_close * (1 - TRAILING_DISTANCE_PCT / 100)
                        if new_sl > trailing_sl:
                            trailing_sl = new_sl
                else:
                    if cur_close <= initial_entry * (1 - TRAILING_START_PCT / 100):
                        new_sl = cur_close * (1 + TRAILING_DISTANCE_PCT / 100)
                        if new_sl < trailing_sl:
                            trailing_sl = new_sl

            # 3) Averaging
            if with_avg and AVG_ENABLED and avg_count < len(AVG_LEVELS_PCT):
                lvl_pct = AVG_LEVELS_PCT[avg_count]
                if side == "SHORT":
                    trigger = initial_entry * (1 + lvl_pct / 100)
                    should = hi >= trigger
                    fill_price = trigger
                else:
                    trigger = initial_entry * (1 - lvl_pct / 100)
                    should = lo <= trigger
                    fill_price = trigger

                if should:
                    add_size = AVG_SIZE_MULT[avg_count]
                    new_total = cur_size + add_size
                    cur_entry = (cur_entry * cur_size + fill_price * add_size) / new_total
                    cur_size = new_total
                    avg_entries.append({"price": fill_price, "size": add_size})
                    avg_count += 1

        # ─── Post-loop ───
        if outcome is None:
            outcome = "OPEN"
            exit_i = min(entry_i + MAX_HOLD_BARS, n - 1)
            exit_price = c4h[exit_i]["close"]

        hard_sl_risk = abs(hard_sl - initial_entry)
        if hard_sl_risk <= 0:
            continue

        if side == "SHORT":
            pnl_price = (cur_entry - exit_price)
        else:
            pnl_price = (exit_price - cur_entry)

        # Commission: fee on entry notional + fee on exit notional
        # In price units: (entry + exit) * fee_rate * cur_size / cur_size
        commission_price = (cur_entry + exit_price) * (COMMISSION_PCT / 100)
        pnl_price_net = pnl_price - commission_price

        r_mult = (pnl_price_net * cur_size) / hard_sl_risk

        results.append({
            "symbol": sym, "side": side,
            "entry_ts": c4h[entry_i]["ts"], "entry": initial_entry,
            "sl": sl, "tp": tp, "hard_sl": hard_sl,
            "exit_ts": c4h[exit_i]["ts"], "exit_price": exit_price,
            "outcome": outcome, "r": r_mult,
            "bars_held": exit_i - entry_i,
            "avg_count": avg_count,
        })

    return results

def summarize(trades, label):
    if not trades:
        return {"label": label, "n": 0}
    tp_wins = [t for t in trades if t["outcome"] == "TP"]
    trail_wins = [t for t in trades if t["outcome"] == "TRAIL_SL" and t["r"] > 0]
    trail_losses = [t for t in trades if t["outcome"] == "TRAIL_SL" and t["r"] <= 0]
    hard_losses = [t for t in trades if t["outcome"] == "HARD_SL"]
    opens = [t for t in trades if t["outcome"] == "OPEN"]

    wins = tp_wins + trail_wins
    losses = hard_losses + trail_losses

    total_r = sum(t["r"] for t in trades)
    win_r = sum(t["r"] for t in wins)
    loss_r = sum(t["r"] for t in losses)
    pf = (win_r / abs(loss_r)) if loss_r < 0 else (float("inf") if win_r > 0 else 0)
    closed = len(wins) + len(losses)
    wr = len(wins) / closed * 100 if closed else 0
    return {
        "label": label, "n": len(trades),
        "wins": len(wins), "losses": len(losses), "opens": len(opens),
        "tp": len(tp_wins), "trail": len(trail_wins) + len(trail_losses),
        "hard": len(hard_losses),
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
    print(f"  TP/TRAIL/HARD: {s['tp']}/{s['trail']}/{s['hard']}")
    print(f"  win rate:      {s['wr']:.1f}%")
    print(f"  total R:       {s['total_r']:+.2f}")
    print(f"  avg R/trade:   {s['avg_r']:+.3f}")
    print(f"  avg win:       {s['avg_win']:+.2f} R")
    print(f"  avg loss:      {s['avg_loss']:+.2f} R")
    print(f"  profit factor: {s['pf']:.2f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tf", default="4H", choices=["4H"])  # strategy is 4H-only
    ap.add_argument("--with-avg", action="store_true", help="enable averaging")
    ap.add_argument("--symbols", type=str, default="",
                    help="comma-separated symbols (e.g. ETHUSDT,SOLUSDT)")
    args = ap.parse_args()
    if args.symbols:
        active_symbols = [s.strip().upper() for s in args.symbols.split(",")]
    else:
        active_symbols = SYMBOLS

    print(f"[PB-BT] pullback strategy backtest")
    print(f"[PB-BT] channel={TIMEFRAME} period={CHANNEL_PERIOD}  "
          f"width=[{MIN_WIDTH_PCT},{MAX_WIDTH_PCT}]  "
          f"LONG<= {LONG_MAX_POS}  SHORT>= {SHORT_MIN_POS}  "
          f"SL_buf={SL_BUFFER_PCT}%  hardSL={HARD_SL_PCT}%  "
          f"avg={'ON' if args.with_avg else 'OFF'}\n")
    print(f"[PB-BT] commission={COMMISSION_PCT}% per side (round-trip={COMMISSION_PCT*2}%)")
    
    # BTC 4H
    btc_path = os.path.join(DATA_DIR, "BTCUSDT_4H.csv")
    if not os.path.exists(btc_path):
        print(f"ERROR: {btc_path} missing — run download_historical first"); sys.exit(1)
    btc4h = load_csv(btc_path)
    print(f"[PB-BT] BTC 4H loaded: {len(btc4h)} candles\n")

    all_trades = []
    per_symbol = {}

    for sym in active_symbols:
        path = os.path.join(DATA_DIR, f"{sym}_4H.csv")
        if not os.path.exists(path):
            print(f"[BT] {sym:10s} MISSING"); continue
        c4h = load_csv(path)
        trades = backtest_symbol(sym, c4h, btc4h, with_avg=args.with_avg)
        per_symbol[sym] = trades
        all_trades.extend(trades)
        print(f"[BT] {sym:10s} setups: {len(trades):3d}")

    print("\n" + "=" * 70)
    print("PULLBACK STRATEGY — BACKTEST SUMMARY")
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