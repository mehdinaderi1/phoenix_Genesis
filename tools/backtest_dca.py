"""
tools/backtest_dca.py — Backtest DCA + Buy-the-Dip strategy on spot

Logic:
  - Reference high = highest close of last 42 x 4H candles (7 days)
  - Trigger ladder: -10%, -15%, -20%, -25%, -30% from that high
  - 5 steps, each = 20% of total allocation per symbol
  - Exit: 50% at +20% from avg entry, 50% at +40% from avg entry
  - Timeout: 60 days (360 x 4H bars) — close at market if not hit

Usage:
    python tools/backtest_dca.py
    python tools/backtest_dca.py --symbols "ETHUSDT,SOLUSDT"
"""
import os, sys, csv, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = "data/historical"
DEFAULT_SYMBOLS = [
    "ETHUSDT","SOLUSDT","ARBUSDT","OPUSDT","DOGEUSDT","PEPEUSDT",
    "AAVEUSDT","INJUSDT","FETUSDT","WLDUSDT","ZECUSDT","XMRUSDT",
    "XRPUSDT","DASHUSDT",
]

# ─── Config ───
REF_HIGH_LOOKBACK = 42      # 7 days x 6 (4H)
LADDER_PCT         = [10, 15, 20, 25, 30]   # drop thresholds
LADDER_WEIGHT      = [0.2, 0.2, 0.2, 0.2, 0.2]  # each step 20%
TP1_PCT            = 20     # first take-profit: +20% from avg entry
TP2_PCT            = 40     # second take-profit: +40% from avg entry
TP1_FRACTION       = 0.5    # sell half at TP1
TIMEOUT_BARS       = 360    # 60 days on 4H
COMMISSION_PCT     = 0.1    # 0.1% per side (spot) = 0.2% round-trip


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


def backtest_symbol(sym, c4h):
    n = len(c4h)
    trades = []
    i = REF_HIGH_LOOKBACK

    while i < n - 1:
        # Reference high over last 7 days
        ref_high = max(c["high"] for c in c4h[i - REF_HIGH_LOOKBACK:i])
        if ref_high <= 0:
            i += 1
            continue

        # Entry ladder tracking
        filled_levels = 0
        total_size = 0.0
        total_cost = 0.0
        tp1_taken = False
        entry_i = None
        exit_reason = None
        exit_price = None
        exit_i = None

        for k in range(i, min(i + TIMEOUT_BARS, n)):
            c = c4h[k]
            lo = c["low"]

            # Check each unfilled level
            while filled_levels < len(LADDER_PCT):
                trigger_price = ref_high * (1 - LADDER_PCT[filled_levels] / 100)
                if lo <= trigger_price:
                    weight = LADDER_WEIGHT[filled_levels]
                    # Buy at trigger price (assume filled)
                    buy_price = trigger_price
                    total_size += weight
                    total_cost += weight * buy_price
                    if entry_i is None:
                        entry_i = k
                    filled_levels += 1
                else:
                    break

            if filled_levels == 0:
                continue

            # Compute avg entry
            avg_entry = total_cost / total_size if total_size > 0 else 0
            hi = c["high"]
            close = c["close"]

            # TP1: sell half at +20%
            if not tp1_taken:
                tp1_price = avg_entry * (1 + TP1_PCT / 100)
                if hi >= tp1_price:
                    # Realize half
                    sell_size = total_size * TP1_FRACTION
                    realized_pnl = (tp1_price - avg_entry) * sell_size
                    commission = (avg_entry + tp1_price) * (COMMISSION_PCT / 100) * sell_size
                    trades.append({
                        "symbol": sym, "entry_ts": c4h[entry_i]["ts"],
                        "exit_ts": c["ts"], "avg_entry": avg_entry,
                        "exit_price": tp1_price, "reason": "TP1",
                        "size": sell_size, "pnl_pct": (tp1_price - avg_entry) / avg_entry * 100,
                        "pnl_net": realized_pnl - commission,
                        "levels": filled_levels,
                    })
                    total_size -= sell_size
                    total_cost = avg_entry * total_size  # keep avg unchanged
                    tp1_taken = True

            if total_size <= 1e-9:
                exit_i = k
                exit_reason = "TP1_FULL"
                break

            # TP2: sell remaining at +40%
            tp2_price = avg_entry * (1 + TP2_PCT / 100)
            if hi >= tp2_price:
                realized_pnl = (tp2_price - avg_entry) * total_size
                commission = (avg_entry + tp2_price) * (COMMISSION_PCT / 100) * total_size
                trades.append({
                    "symbol": sym, "entry_ts": c4h[entry_i]["ts"],
                    "exit_ts": c["ts"], "avg_entry": avg_entry,
                    "exit_price": tp2_price, "reason": "TP2",
                    "size": total_size, "pnl_pct": (tp2_price - avg_entry) / avg_entry * 100,
                    "pnl_net": realized_pnl - commission,
                    "levels": filled_levels,
                })
                exit_i = k
                exit_reason = "TP2"
                break
        else:
            # Timeout — close at market
            if filled_levels > 0 and total_size > 0:
                k_last = min(i + TIMEOUT_BARS - 1, n - 1)
                close_px = c4h[k_last]["close"]
                avg_entry = total_cost / total_size
                realized_pnl = (close_px - avg_entry) * total_size
                commission = (avg_entry + close_px) * (COMMISSION_PCT / 100) * total_size
                trades.append({
                    "symbol": sym, "entry_ts": c4h[entry_i]["ts"],
                    "exit_ts": c4h[k_last]["ts"], "avg_entry": avg_entry,
                    "exit_price": close_px, "reason": "TIMEOUT",
                    "size": total_size, "pnl_pct": (close_px - avg_entry) / avg_entry * 100,
                    "pnl_net": realized_pnl - commission,
                    "levels": filled_levels,
                })
                exit_i = k_last

        if exit_i is None or exit_i <= i:
            i += 1
        else:
            i = exit_i + 1

    return trades


def summarize(trades, label):
    if not trades:
        return {"label": label, "n": 0}
    wins = [t for t in trades if t["pnl_net"] > 0]
    losses = [t for t in trades if t["pnl_net"] <= 0]
    # Use percentage return per trade (normalized to equal weight)
    def pct_return(t):
        return (t["exit_price"] - t["avg_entry"]) / t["avg_entry"] * 100

    total_pnl = sum(pct_return(t) for t in trades)
    win_pnl = sum(pct_return(t) for t in wins)
    loss_pnl = sum(pct_return(t) for t in losses)
    pf = (win_pnl / abs(loss_pnl)) if loss_pnl < 0 else (float("inf") if win_pnl > 0 else 0)
    wr = len(wins) / len(trades) * 100 if trades else 0
    return {
        "label": label, "n": len(trades),
        "wins": len(wins), "losses": len(losses),
        "wr": wr, "total_pnl": total_pnl,
        "avg_pnl": total_pnl / len(trades),
        "avg_win": win_pnl / len(wins) if wins else 0,
        "avg_loss": loss_pnl / len(losses) if losses else 0,
        "pf": pf,
    }


def print_stats(s):
    if s["n"] == 0:
        print(f"\n[{s['label']}] no trades"); return
    print(f"\n[{s['label']}]")
    print(f"  trades:    {s['n']}")
    print(f"  W/L:       {s['wins']}/{s['losses']}")
    print(f"  win rate:  {s['wr']:.1f}%")
    print(f"  total PnL: {s['total_pnl']:+.4f} (per unit weight)")
    print(f"  avg PnL:   {s['avg_pnl']:+.4f}")
    print(f"  avg win:   {s['avg_win']:+.4f}")
    print(f"  avg loss:  {s['avg_loss']:+.4f}")
    print(f"  PF:        {s['pf']:.2f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", type=str, default="")
    args = ap.parse_args()

    symbols = [s.strip().upper() for s in args.symbols.split(",")] if args.symbols else DEFAULT_SYMBOLS

    print(f"[DCA-BT] ladder={LADDER_PCT} weights={LADDER_WEIGHT}")
    print(f"[DCA-BT] TP1=+{TP1_PCT}% (half)  TP2=+{TP2_PCT}% (rest)  timeout={TIMEOUT_BARS} bars")
    print(f"[DCA-BT] commission={COMMISSION_PCT}% per side (round-trip={COMMISSION_PCT*2}%)")
    print(f"[DCA-BT] symbols: {len(symbols)}\n")

    all_trades = []
    per_symbol = {}
    for sym in symbols:
        path = os.path.join(DATA_DIR, f"{sym}_4H.csv")
        if not os.path.exists(path):
            print(f"[BT] {sym:12s} MISSING"); continue
        c4h = load_csv(path)
        trades = backtest_symbol(sym, c4h)
        per_symbol[sym] = trades
        all_trades.extend(trades)
        print(f"[BT] {sym:12s} trades: {len(trades):3d}  ({len(c4h)} candles)")

    print("\n" + "=" * 70)
    print("DCA + BUY-THE-DIP — SPOT BACKTEST")
    print("=" * 70)
    print_stats(summarize(all_trades, "ALL"))

    print("\n" + "-" * 70)
    print("Per symbol:")
    print(f"  {'SYMBOL':10s} {'N':>4s} {'W/L':>7s} {'WR%':>6s} {'TotPnL':>10s} {'PF':>6s}")
    for sym, t in sorted(per_symbol.items(), key=lambda kv: -len(kv[1])):
        if not t: continue
        s = summarize(t, sym)
        print(f"  {sym:10s} {s['n']:>4d} {s['wins']:>3d}/{s['losses']:<3d} "
              f"{s['wr']:>6.1f} {s['total_pnl']:>+10.4f} {s['pf']:>6.2f}")


if __name__ == "__main__":
    main()