"""
tools/backtest_ratio_filter.py — Sensitivity test for ratio filter windows
"""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.futures_strategy_runner import (
    CHANNEL_PERIOD, MIN_WIDTH_PCT, MAX_WIDTH_PCT,
    LONG_MAX_POS, SL_BUFFER_PCT, HARD_SL_PCT,
    AVG_ENABLED, AVG_LEVELS_PCT, AVG_SIZE_MULT,
    compute_channel, btc_direction, candle_sig_with_volume,
    _close, _high, _low,
)

DATA_DIR = "data/historical"
MAX_HOLD_BARS = 400
COMMISSION_PCT = 0.06  # per side
SYMBOL_RISK_MULT = {"OPUSDT": 0.5}
SYMBOLS = ["ETHUSDT","OPUSDT","DOGEUSDT","PEPEUSDT","AAVEUSDT","INJUSDT",
           "FETUSDT","WLDUSDT","ZECUSDT","XRPUSDT","DASHUSDT"]

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

def load_ratio(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({"ts": int(float(r["timestamp"])), "ratio": float(r["ratio"])})
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

def backtest_symbol(sym, c4h, btc4h, ratio, window, with_avg=False):
    n = len(c4h)
    results = []
    start = max(CHANNEL_PERIOD + 20, 60)

    for i in range(start, n - 1):
        ts = c4h[i]["ts"]

        idx_btc = find_idx(btc4h, ts)
        if idx_btc < 60: continue
        btc_dir = btc_direction(btc4h[:idx_btc])
        if btc_dir == "UNKNOWN": continue

        # فیلتر نسبت با پنجره مشخص
        idx_ratio = find_idx(ratio, ts)
        if idx_ratio < window:
            ratio_ok = False
        else:
            ratio_slice = [r["ratio"] for r in ratio[idx_ratio - window:idx_ratio]]
            if len(ratio_slice) >= 2:
                ratio_ok = ratio_slice[-1] > ratio_slice[0]
            else:
                ratio_ok = False

        if not ratio_ok: continue

        ch = compute_channel(c4h[:i], CHANNEL_PERIOD)
        if not ch: continue
        if ch["width_pct"] < MIN_WIDTH_PCT or ch["width_pct"] > MAX_WIDTH_PCT: continue

        price = c4h[i - 1]["close"]
        rng = ch["upper"] - ch["lower"]
        if rng <= 0: continue
        pos_pct = (price - ch["lower"]) / rng * 100

        window_candles = c4h[max(0, i - 15):i]
        sig = candle_sig_with_volume(window_candles, window=10)
        if not sig: continue

        side = None
        if btc_dir in ("UP", "FLAT") and pos_pct <= LONG_MAX_POS and \
           sig["lower_wick_pct"] >= 30 and sig.get("volume_confirmed", False):
            side = "LONG"

        if side is None: continue

        entry_i = i
        if entry_i >= n - 1: break
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
            outcome = "OPEN"; exit_i = min(entry_i + MAX_HOLD_BARS, n - 1)
            exit_price = c4h[exit_i]["close"]

        risk = abs(hard_sl - initial_entry)
        if risk <= 0: continue
        pnl = (exit_price - cur_entry)
        commission = (cur_entry + exit_price) * (COMMISSION_PCT / 100)
        r = ((pnl - commission) * cur_size) / risk

        r_mult = SYMBOL_RISK_MULT.get(sym, 1.0)
        r *= r_mult

        results.append({"symbol": sym, "side": side, "outcome": outcome, "r": r})
    return results

def summarize(trades, label):
    if not trades: return {"label": label, "n": 0}
    wins = [t for t in trades if t["outcome"] == "TP"]
    losses = [t for t in trades if t["outcome"] == "HARD_SL"]
    opens = [t for t in trades if t["outcome"] == "OPEN"]
    total_r = sum(t["r"] for t in trades)
    wr = len(wins)/(len(wins)+len(losses))*100 if (wins or losses) else 0
    win_r = sum(t["r"] for t in wins); loss_r = sum(t["r"] for t in losses)
    pf = (win_r/abs(loss_r)) if loss_r < 0 else (float('inf') if win_r>0 else 0)
    return {"label": label, "n": len(trades), "wins": len(wins), "losses": len(losses),
            "opens": len(opens), "wr": wr, "total_r": total_r,
            "avg_r": total_r/len(trades), "pf": pf}

def main():
    windows = [5, 10, 15, 20, 30]
    btc4h_path = os.path.join(DATA_DIR, "BTCUSDT_4H.csv")
    btc4h = load_csv(btc4h_path) if os.path.exists(btc4h_path) else []

    # ذخیره نتایج برای هر پنجره
    all_results = {w: [] for w in windows}

    for sym in SYMBOLS:
        path4h = os.path.join(DATA_DIR, f"{sym}_4H.csv")
        path_ratio = os.path.join(DATA_DIR, f"{sym.replace('USDT','')}_BTC_ratio.csv")
        if not os.path.exists(path4h) or not os.path.exists(path_ratio):
            continue
        c4h = load_csv(path4h)
        ratio = load_ratio(path_ratio)

        for w in windows:
            trades = backtest_symbol(sym, c4h, btc4h, ratio, w, with_avg=True)
            all_results[w].extend(trades)
        print(f"[BT] {sym:10s} done")

    print("\n" + "=" * 70)
    print("SENSITIVITY TEST — Ratio Filter Window Size")
    print("=" * 70)

    for w in windows:
        stats = summarize(all_results[w], f"window={w}")
        print(f"\n[Window = {w} candles]")
        if stats["n"] == 0:
            print("  no trades")
            continue
        print(f"  trades: {stats['n']}  W/L/OPEN: {stats['wins']}/{stats['losses']}/{stats['opens']}")
        print(f"  win rate: {stats['wr']:.1f}%")
        print(f"  total R: {stats['total_r']:+.2f}  avg R: {stats['avg_r']:+.3f}")
        print(f"  PF: {stats['pf']:.2f}")

if __name__ == "__main__":
    main()