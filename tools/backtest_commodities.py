"""
tools/backtest_commodities.py — Backtest pullback strategy on commodities

Uses the same logic as futures_strategy_runner._detect, but only on
GOLDUSDT / SILVERUSDT / OILUSDT (TradFi perpetuals on XT).

Usage:
    python tools/backtest_commodities.py
    python tools/backtest_commodities.py --with-avg
"""
import os, sys, csv, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.futures_strategy_runner import (
    CHANNEL_PERIOD, MIN_WIDTH_PCT, MAX_WIDTH_PCT,
    LONG_MAX_POS, SHORT_MIN_POS, SL_BUFFER_PCT, HARD_SL_PCT,
    AVG_ENABLED, AVG_LEVELS_PCT, AVG_SIZE_MULT,
    compute_channel, btc_direction, candle_sig_with_volume,
)

DATA_DIR = "data/historical"
COMMODITIES = ["GOLDUSDT", "SILVERUSDT", "OILUSDT"]
MAX_HOLD_BARS = 400
TRAILING_ENABLED = False
COMMISSION_PCT = 0.05  # per side


def load_csv(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "ts": int(float(r["timestamp"])),
                "open": float(r["open"]), "high": float(r["high"]),
                "low": float(r["low"]), "close": float(r["close"]),
                "volume": float(r["volume"]),
            })
    rows.sort(key=lambda x: x["ts"])
    return rows


def find_idx(candles, ts):
    lo, hi, ans = 0, len(candles) - 1, -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if candles[mid]["ts"] <= ts:
            ans = mid; lo = mid + 1
        else:
            hi = mid - 1
    return ans


def backtest_symbol(sym, c4h, btc4h, with_avg=False):
    n = len(c4h)
    results = []
    start = max(CHANNEL_PERIOD + 20, 60)

    for i in range(start, n - 1):
        ts = c4h[i]["ts"]

        # ─── فیلتر مستقل: روند خود کامودیتی (نه BTC) ───
        own_dir = btc_direction(c4h[:i])
        if own_dir == "UNKNOWN":
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

        # ─── تصمیم ورود ───
        side = None
        if own_dir in ("UP", "FLAT") and pos_pct <= LONG_MAX_POS \
           and sig["lower_wick_pct"] >= 30 and sig.get("volume_confirmed", False):
            side = "LONG"

        if side is None:
            continue

        entry_i = i
        if entry_i >= n - 1:
            break
        initial_entry = c4h[entry_i]["open"]
        cur_entry = initial_entry
        cur_size = 1.0
        sl = ch["lower"] * (1 - SL_BUFFER_PCT / 100)
        tp = ch["mid"]
        hard_sl = initial_entry * (1 - HARD_SL_PCT / 100)

        avg_count = 0
        outcome = None
        exit_price = None
        exit_i = None

        for k in range(entry_i + 1, min(entry_i + 1 + MAX_HOLD_BARS, n)):
            c = c4h[k]
            hi, lo = c["high"], c["low"]

            if lo <= hard_sl:
                outcome, exit_price, exit_i = "HARD_SL", hard_sl, k; break
            if hi >= tp:
                outcome, exit_price, exit_i = "TP", tp, k; break

            if with_avg and AVG_ENABLED and avg_count < len(AVG_LEVELS_PCT):
                lvl = AVG_LEVELS_PCT[avg_count]
                trigger = initial_entry * (1 - lvl / 100)
                if lo <= trigger:
                    add = AVG_SIZE_MULT[avg_count]
                    new_total = cur_size + add
                    cur_entry = (cur_entry * cur_size + trigger * add) / new_total
                    cur_size = new_total
                    avg_count += 1

        if outcome is None:
            outcome = "OPEN"
            exit_i = min(entry_i + MAX_HOLD_BARS, n - 1)
            exit_price = c4h[exit_i]["close"]

        risk = abs(hard_sl - initial_entry)
        if risk <= 0:
            continue
        pnl = (exit_price - cur_entry)
        commission = (cur_entry + exit_price) * (COMMISSION_PCT / 100)
        r = ((pnl - commission) * cur_size) / risk

        results.append({
            "symbol": sym, "side": side, "entry": initial_entry,
            "exit": exit_price, "outcome": outcome, "r": r,
            "avg_count": avg_count, "entry_ts": c4h[entry_i]["ts"],
        })

    return results


def summarize(trades, label):
    if not trades: return {"label": label, "n": 0}
    wins = [t for t in trades if t["r"] > 0]
    losses = [t for t in trades if t["r"] <= 0 and t["outcome"] != "OPEN"]
    total_r = sum(t["r"] for t in trades)
    win_r = sum(t["r"] for t in wins)
    loss_r = sum(t["r"] for t in losses)
    pf = (win_r / abs(loss_r)) if loss_r < 0 else (float("inf") if win_r > 0 else 0)
    wr = len(wins) / (len(wins) + len(losses)) * 100 if (wins or losses) else 0
    return {"label": label, "n": len(trades), "wins": len(wins),
            "losses": len(losses), "wr": wr, "total_r": total_r,
            "avg_r": total_r/len(trades), "pf": pf}


def print_stats(s):
    if s["n"] == 0:
        print(f"\n[{s['label']}] no trades"); return
    print(f"\n[{s['label']}]")
    print(f"  trades:  {s['n']}")
    print(f"  W/L:     {s['wins']}/{s['losses']}")
    print(f"  win rate:{s['wr']:.1f}%")
    print(f"  total R: {s['total_r']:+.2f}")
    print(f"  avg R:   {s['avg_r']:+.3f}")
    print(f"  PF:      {s['pf']:.2f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-avg", action="store_true")
    args = ap.parse_args()

    btc_path = os.path.join(DATA_DIR, "BTCUSDT_4H.csv")
    if not os.path.exists(btc_path):
        print("ERROR: BTCUSDT_4H.csv missing"); sys.exit(1)
    btc4h = load_csv(btc_path)
    print(f"[CMD-BT] BTC 4H: {len(btc4h)} candles")
    print(f"[CMD-BT] commodities: {COMMODITIES}")
    print(f"[CMD-BT] avg={'ON' if args.with_avg else 'OFF'}  commission={COMMISSION_PCT*2}% round-trip\n")

    all_trades = []
    for sym in COMMODITIES:
        path = os.path.join(DATA_DIR, f"{sym}_4H.csv")
        if not os.path.exists(path):
            print(f"[BT] {sym:12s} MISSING"); continue
        c4h = load_csv(path)
        trades = backtest_symbol(sym, c4h, btc4h, with_avg=args.with_avg)
        all_trades.extend(trades)
        print(f"[BT] {sym:12s} setups: {len(trades):3d}  ({len(c4h)} candles)")

    print("\n" + "=" * 70)
    print("COMMODITIES — PULLBACK BACKTEST")
    print("=" * 70)
    print_stats(summarize(all_trades, "ALL commodities"))

    print("\n" + "-" * 70)
    print("Per commodity:")
    for sym in COMMODITIES:
        t = [x for x in all_trades if x["symbol"] == sym]
        if t:
            s = summarize(t, sym)
            print(f"  {sym:12s} N={s['n']:3d}  W/L={s['wins']}/{s['losses']}  "
                  f"WR={s['wr']:5.1f}%  TotR={s['total_r']:+7.2f}  PF={s['pf']:.2f}")


if __name__ == "__main__":
    main()