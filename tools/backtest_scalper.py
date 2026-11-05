"""
Backtest scalper on 15m data with REAL transaction fees + funding fees.
"""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SYMBOLS = ["ETHUSDT","OPUSDT","DOGEUSDT","PEPEUSDT","AAVEUSDT","INJUSDT",
           "FETUSDT","WLDUSDT","ZECUSDT","XRPUSDT","DASHUSDT"]

# ─── Config ───
IMPULSE_BARS   = 3        
IMPULSE_MIN_PCT = 1.5     
SL_PCT         = 1.2      # پهن‌تر برای جلوگیری از نویز ۱۵ دقیقه
TP1_MULT       = 1.5      # TP = 1.8%
TIMEOUT_BARS   = 8        # 8 * 15m = 2 ساعت

# کارمزدها
TX_FEE_PCT     = 0.06     # 0.06% برای هر طرف (0.12% کل)
FUNDING_PCT_8H = 0.01     # 0.01% هر 8 ساعت (برای شبیه‌سازی)

def load(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({"ts": int(float(r["timestamp"])),
                         "open": float(r["open"]), "high": float(r["high"]),
                         "low": float(r["low"]), "close": float(r["close"]),
                         "volume": float(r["volume"])})
    rows.sort(key=lambda x: x["ts"])
    return rows

def backtest(candles, mode, trend_index=None):
    n = len(candles)
    if n < 20: return []
    trades = []
    i = IMPULSE_BARS
    
    while i < n - TIMEOUT_BARS - 1:
        last3 = candles[i-IMPULSE_BARS:i]
        pct_sum = (last3[-1]["close"] - last3[0]["open"]) / last3[0]["open"] * 100
        all_green = all(c["close"] > c["open"] for c in last3)
        all_red   = all(c["close"] < c["open"] for c in last3)
        
        if not (all_green or all_red): i += 1; continue
        if abs(pct_sum) < IMPULSE_MIN_PCT: i += 1; continue

        recent_vols = [c["volume"] for c in candles[i-10:i] if c["volume"] > 0]
        avg_vol = sum(recent_vols) / len(recent_vols) if recent_vols else 0
        if avg_vol > 0 and last3[-1]["volume"] < 1.2 * avg_vol: i += 1; continue

        direction = "UP" if all_green else "DOWN"
        side = "LONG" if (mode == "momentum" and direction == "UP") or (mode == "reversion" and direction == "DOWN") else "SHORT"
        
        # فیلتر روند (اختیاری)
        if trend_index is not None:
            trend_1h = find_trend(trend_index, candles[i]["ts"])
            if mode == "momentum":
                if trend_1h == "UP" and side != "LONG": i += 1; continue
                if trend_1h == "DOWN" and side != "SHORT": i += 1; continue
            else:
                if trend_1h != "FLAT": i += 1; continue

        entry = candles[i]["open"]
        if side == "LONG":
            sl = entry * (1 - SL_PCT / 100)
            tp = entry * (1 + TP1_MULT * SL_PCT / 100)
        else:
            sl = entry * (1 + SL_PCT / 100)
            tp = entry * (1 - TP1_MULT * SL_PCT / 100)

        outcome, exit_price, exit_i = None, None, None
        for k in range(i + 1, min(i + 1 + TIMEOUT_BARS, n)):
            c = candles[k]
            if side == "LONG":
                if c["low"] <= sl: outcome, exit_price, exit_i = "LOSS", sl, k; break
                if c["high"] >= tp: outcome, exit_price, exit_i = "WIN", tp, k; break
            else:
                if c["high"] >= sl: outcome, exit_price, exit_i = "LOSS", sl, k; break
                if c["low"] <= tp: outcome, exit_price, exit_i = "WIN", tp, k; break
        if outcome is None:
            outcome = "OPEN"; exit_i = min(i + TIMEOUT_BARS, n - 1)
            exit_price = candles[exit_i]["close"]

        # ─── محاسبه سود/ضرر خالص با کارمزدها ───
        pnl_raw = (exit_price - entry) if side == "LONG" else (entry - exit_price)
        
        # ۱. کارمزد تراکنش (ورود + خروج)
        tx_fee = (entry + exit_price) * (TX_FEE_PCT / 100)
        
        # ۲. کارمزد فاندینگ (به ازای هر ساعت)
        hours_held = (candles[exit_i]["ts"] - candles[i]["ts"]) / 3600
        # فرض: در 8 ساعت 0.01% (میانگین)
        funding_fee = entry * (FUNDING_PCT_8H / 100) * (hours_held / 8)
        
        pnl_net = pnl_raw - tx_fee - funding_fee
        r = pnl_net / (entry * SL_PCT / 100)
        
        trades.append({"side": side, "outcome": outcome, "r": r})
        i = exit_i + 1
    return trades

def build_trend_index(c1h):
    trends = []
    closes = [c["close"] for c in c1h]
    for i in range(len(c1h)):
        if i < 60:
            trends.append((c1h[i]["ts"], "UNKNOWN")); continue
        e20 = sum(closes[i-20:i]) / 20
        e50 = sum(closes[i-50:i]) / 50
        diff = (e20 - e50) / e50 * 100
        if diff > 0.5:   trends.append((c1h[i]["ts"], "UP"))
        elif diff < -0.5: trends.append((c1h[i]["ts"], "DOWN"))
        else:             trends.append((c1h[i]["ts"], "FLAT"))
    return trends

def find_trend(trend_index, ts):
    lo, hi, ans = 0, len(trend_index) - 1, -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if trend_index[mid][0] <= ts: ans = mid; lo = mid + 1
        else: hi = mid - 1
    if ans < 0: return "UNKNOWN"
    return trend_index[ans][1]

def summarize(trades, label):
    if not trades: return {"label": label, "n": 0}
    wins = [t for t in trades if t["outcome"]=="WIN"]
    losses = [t for t in trades if t["outcome"]=="LOSS"]
    opens = [t for t in trades if t["outcome"]=="OPEN"]
    total_r = sum(t["r"] for t in trades)
    wr = len(wins)/(len(wins)+len(losses))*100 if (wins or losses) else 0
    win_r = sum(t["r"] for t in wins); loss_r = sum(t["r"] for t in losses)
    pf = (win_r/abs(loss_r)) if loss_r < 0 else (float('inf') if win_r>0 else 0)
    return {"label": label, "n": len(trades), "wins": len(wins), "losses": len(losses),
            "opens": len(opens), "wr": wr, "total_r": total_r,
            "avg_r": total_r/len(trades) if len(trades)>0 else 0, "pf": pf}

def print_stats(s):
    if s["n"]==0: print(f"\n[{s['label']}] no trades"); return
    print(f"\n[{s['label']}]")
    print(f"  trades: {s['n']}  W/L/OPEN: {s['wins']}/{s['losses']}/{s['opens']}")
    print(f"  win rate: {s['wr']:.1f}%")
    print(f"  total R: {s['total_r']:+.2f}  avg R: {s['avg_r']:+.3f}")
    print(f"  PF: {s['pf']:.2f}")

def main():
    all_mom, all_rev = [], []
    all_mom_f, all_rev_f = [], []

    for sym in SYMBOLS:
        path15 = f"data/historical/{sym}_15m.csv"
        path1h = f"data/historical/{sym}_1H.csv"
        if not os.path.exists(path15): continue

        c15 = load(path15)
        trend_idx = None
        if os.path.exists(path1h):
            c1h = load(path1h)
            trend_idx = build_trend_index(c1h)

        all_mom.extend(backtest(c15, "momentum"))
        all_rev.extend(backtest(c15, "reversion"))
        if trend_idx:
            all_mom_f.extend(backtest(c15, "momentum", trend_index=trend_idx))
            all_rev_f.extend(backtest(c15, "reversion", trend_index=trend_idx))

        print(f"[BT] {sym:10s} loaded.")

    print("\n" + "=" * 70)
    print("SCALPER 15m — WITH TRANSACTION & FUNDING FEES")
    print("=" * 70)

    print("\n=== MOMENTUM ===")
    print_stats(summarize(all_mom, "baseline (no filter)"))
    print_stats(summarize(all_mom_f, "+1H trend filter"))

    print("\n=== REVERSION ===")
    print_stats(summarize(all_rev, "baseline (no filter)"))
    print_stats(summarize(all_rev_f, "+1H FLAT filter"))

if __name__ == "__main__":
    main()