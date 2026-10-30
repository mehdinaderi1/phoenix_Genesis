"""
tools/backtest_detector.py — Walk-forward backtest of break-retest detector

Loads CSVs from data/historical/, walks forward in time on 1H candles,
computes 4H channel using only past data, applies the same detector logic
used live, and simulates each trade forward to SL/TP.

Usage:
    python tools/backtest_detector.py
    python tools/backtest_detector.py --max-lookahead 200
    python tools/backtest_detector.py --csv data/backtest_trades.csv
"""
import os, sys, csv, argparse
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exchanges.xt_exchange import XTExchange
from tools.futures_strategy_runner import (
    SYMBOLS, CHANNEL_PERIOD, compute_channel,
    candle_sig_with_volume, btc_direction,
)
from tools.break_retest_detector import (
    BREAK_WINDOW, MIN_BREAK_AGE,
    detect_break_retest,
)

DATA_DIR = "data/historical"
WARMUP_1H = 100  # skip first N 1H candles (need BREAK_WINDOW + buffer)


def load_csv(path):
    rows = []
    with open(path, "r", newline="") as f:
        for row in csv.DictReader(f):
            rows.append({
                "timestamp": int(float(row["timestamp"])),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
            })
    rows.sort(key=lambda x: x["timestamp"])
    return rows


def find_4h_idx(candles_4h, ts_1h):
    """Binary search: last 4H candle with ts <= ts_1h."""
    lo, hi, ans = 0, len(candles_4h) - 1, -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if candles_4h[mid]["timestamp"] <= ts_1h:
            ans = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return ans


def ensure_btc_data():
    """Download BTCUSDT 4H if missing."""
    path = os.path.join(DATA_DIR, "BTCUSDT_4H.csv")
    if os.path.exists(path):
        return load_csv(path)
    print("[BTC] BTCUSDT_4H.csv missing — downloading...")
    spot = XTExchange(timeout=20)
    candles = spot.get_historical_candles("BTCUSDT", "4H", limit=800)
    if not candles:
        print("[BTC] FAILED to download — aborting"); sys.exit(1)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "open", "high", "low", "close", "volume"])
        for c in candles:
            w.writerow([c["timestamp"], c["open"], c["high"], c["low"], c["close"], c["volume"]])
    print(f"[BTC] saved {len(candles)} rows -> {path}")
    return load_csv(path)


def backtest_symbol(sym, c1h, c4h, btc4h, max_lookahead):
    results = []
    n1, n4 = len(c1h), len(c4h)
    if n1 < WARMUP_1H + 10 or n4 < CHANNEL_PERIOD + 20:
        return results

    for i in range(WARMUP_1H, n1):
        ts = c1h[i]["timestamp"]

        # 4H channel — use up to idx_4h - 1 (exclude forming 4H candle)
        idx_4h = find_4h_idx(c4h, ts)
        if idx_4h < CHANNEL_PERIOD + 2:
            continue
        ch = compute_channel(c4h[:idx_4h], CHANNEL_PERIOD)
        if not ch:
            continue

        # BTC direction — exclude forming 4H candle
        idx_btc = find_4h_idx(btc4h, ts)
        if idx_btc < 60:
            continue
        btc_dir = btc_direction(btc4h[:idx_btc])

        # 1H detector — pass window with current candle i as "forming"
        window = c1h[max(0, i - 40):i + 1]
        sig = candle_sig_with_volume(window, window=10)
        if not sig:
            continue
        hit, _ = detect_break_retest(window, ch, sig, btc_dir)
        if not hit:
            continue

        # Simulate forward
        entry = hit["price"]; sl = hit["sl"]; tp = hit["tp"]; side = hit["side"]
        outcome, exit_price, exit_i = None, None, None
        for j in range(i + 1, min(i + 1 + max_lookahead, n1)):
            c = c1h[j]
            if side == "SHORT":
                if c["high"] >= sl: outcome = "LOSS"; exit_price = sl; exit_i = j; break
                if c["low"]  <= tp: outcome = "WIN";  exit_price = tp; exit_i = j; break
            else:
                if c["low"]  <= sl: outcome = "LOSS"; exit_price = sl; exit_i = j; break
                if c["high"] >= tp: outcome = "WIN";  exit_price = tp; exit_i = j; break
        if outcome is None:
            outcome = "OPEN"
            exit_i = min(i + max_lookahead, n1 - 1)
            exit_price = c1h[exit_i]["close"]

        risk = abs(entry - sl)
        if risk <= 0: continue
        r_mult = (entry - exit_price) / risk if side == "SHORT" else (exit_price - entry) / risk

        results.append({
            "symbol": sym, "side": side, "type": hit["setup_type"],
            "entry_ts": ts, "entry": entry, "sl": sl, "tp": tp,
            "exit_price": exit_price, "exit_ts": c1h[exit_i]["timestamp"],
            "bars_held": exit_i - i, "outcome": outcome,
            "r_multiple": r_mult, "rr_planned": hit["rr"],
        })
    return results


def summarize(results, label="ALL"):
    if not results:
        return {"label": label, "total": 0}
    wins   = [r for r in results if r["outcome"] == "WIN"]
    losses = [r for r in results if r["outcome"] == "LOSS"]
    opens  = [r for r in results if r["outcome"] == "OPEN"]
    total_r = sum(r["r_multiple"] for r in results)
    win_r   = sum(r["r_multiple"] for r in wins)
    loss_r  = sum(r["r_multiple"] for r in losses)
    pf = (win_r / abs(loss_r)) if loss_r < 0 else (float("inf") if win_r > 0 else 0)
    wr = (len(wins) / (len(wins) + len(losses)) * 100) if (wins or losses) else 0
    return {
        "label": label, "total": len(results),
        "wins": len(wins), "losses": len(losses), "opens": len(opens),
        "win_rate": wr, "total_r": total_r,
        "avg_r": total_r / len(results),
        "avg_win": win_r / len(wins) if wins else 0,
        "avg_loss": loss_r / len(losses) if losses else 0,
        "profit_factor": pf,
    }


def print_stats(s):
    if s["total"] == 0:
        print(f"\n[{s['label']}] no trades"); return
    print(f"\n[{s['label']}]")
    print(f"  trades:       {s['total']}")
    print(f"  W/L/OPEN:     {s['wins']}/{s['losses']}/{s['opens']}")
    print(f"  win rate:     {s['win_rate']:.1f}%")
    print(f"  total R:      {s['total_r']:+.2f}")
    print(f"  avg R/trade:  {s['avg_r']:+.3f}")
    print(f"  avg win:      {s['avg_win']:+.2f} R")
    print(f"  avg loss:     {s['avg_loss']:+.2f} R")
    print(f"  profit factor:{s['profit_factor']:.2f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-lookahead", type=int, default=150, help="max 1H bars to wait for SL/TP")
    ap.add_argument("--csv", type=str, default="", help="optional: dump all trades to CSV")
    args = ap.parse_args()

    if not os.path.isdir(DATA_DIR):
        print(f"ERROR: {DATA_DIR} missing. Run: python tools\\download_historical.py"); sys.exit(1)

    btc4h = ensure_btc_data()

    all_results = []
    per_symbol = {}
    missing = []

    for sym in SYMBOLS:
        p1 = os.path.join(DATA_DIR, f"{sym}_1H.csv")
        p4 = os.path.join(DATA_DIR, f"{sym}_4H.csv")
        if not (os.path.exists(p1) and os.path.exists(p4)):
            missing.append(sym); continue
        c1h = load_csv(p1); c4h = load_csv(p4)
        res = backtest_symbol(sym, c1h, c4h, btc4h, args.max_lookahead)
        per_symbol[sym] = res
        all_results.extend(res)
        print(f"[BT] {sym:10s} setups: {len(res):3d}")

    if missing:
        print(f"\n[WARN] missing data: {missing}")

    print("\n" + "=" * 70)
    print(f"BACKTEST SUMMARY  (max_lookahead={args.max_lookahead} bars, detector config as-is)")
    print("=" * 70)

    print_stats(summarize(all_results, "ALL"))
    print_stats(summarize([r for r in all_results if r["side"] == "SHORT"], "SHORT only"))
    print_stats(summarize([r for r in all_results if r["side"] == "LONG"],  "LONG only"))
    print_stats(summarize([r for r in all_results if r["type"] == "breakdown_retest"], "breakdown_retest"))
    print_stats(summarize([r for r in all_results if r["type"] == "breakout_retest"],  "breakout_retest"))

    # Per-symbol breakdown (only symbols with trades)
    print("\n" + "-" * 70)
    print("Per symbol:")
    print(f"  {'SYMBOL':10s} {'N':>4s} {'W/L':>7s} {'WR%':>6s} {'TotR':>7s} {'AvgR':>7s}")
    for sym, res in sorted(per_symbol.items(), key=lambda kv: -len(kv[1])):
        if not res: continue
        s = summarize(res)
        print(f"  {sym:10s} {s['total']:>4d} {s['wins']:>3d}/{s['losses']:<3d} "
              f"{s['win_rate']:>6.1f} {s['total_r']:>+7.2f} {s['avg_r']:>+7.3f}")

    # Optional: dump to CSV
    if args.csv and all_results:
        os.makedirs(os.path.dirname(args.csv) or ".", exist_ok=True)
        with open(args.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(all_results[0].keys()))
            w.writeheader(); w.writerows(all_results)
        print(f"\n[CSV] {len(all_results)} trades -> {args.csv}")

def download_paginated(spot, sym, tf, days=90):
    all_candles = []
    end_ts = int(time.time() * 1000)  # اکنون (میلی‌ثانیه)
    start_limit = end_ts - days * 86400 * 1000

    while end_ts > start_limit:
        batch = spot.get_historical_candles(
            sym, tf, limit=800,
            startTime=start_limit,  # ← دقیق به میلی‌ثانیه
            endTime=end_ts
        )
        if not batch:
            break
        all_candles = batch + all_candles  # قدیمی‌ترها را اول بچین
        end_ts = batch[0]["timestamp"] - 1  # یک میلی‌ثانیه قبل از قدیمی‌ترین
        time.sleep(0.25)  # رعایت rate limit (۱۰ درخواست در ثانیه)
    return all_candlesموافقم

if __name__ == "__main__":
    main()