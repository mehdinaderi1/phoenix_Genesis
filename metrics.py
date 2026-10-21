# metrics.py — analyze paper_sessions for win rate, PF, drawdown
import json
from pathlib import Path


def analyze():
    sessions = sorted(Path("data/paper_sessions").glob("*.json"))
    if not sessions:
        print("No sessions found")
        return

    trades = []
    for s in sessions:
        try:
            d = json.loads(s.read_text(encoding="utf-8"))
        except Exception:
            continue
        summary = d.get("summary", {})
        if summary.get("trade_count", 0) == 0:
            continue

        pnl = summary.get("total_pnl", 0.0)
        count = summary.get("trade_count", 0)
        balance = summary.get("balance", 1000.0)

        trades.append({
            "session": s.name,
            "pnl": pnl,
            "count": count,
            "balance": balance,
            "return_pct": (balance - 1000.0) / 1000.0 * 100,
        })

    if not trades:
        print("No closed trades found - need more cycles")
        return

    total_pnl = sum(t["pnl"] for t in trades)
    total_trades = sum(t["count"] for t in trades)
    wins = [t for t in trades if t["pnl"] > 0]
    losses = [t for t in trades if t["pnl"] < 0]

    win_pnl = sum(t["pnl"] for t in wins) if wins else 0
    loss_pnl = abs(sum(t["pnl"] for t in losses)) if losses else 0
    pf = win_pnl / loss_pnl if loss_pnl > 0 else float("inf")

    print()
    print("=" * 60)
    print("PHOENIX GENESIS - METRICS REPORT")
    print("=" * 60)
    print(f"Sessions with trades: {len(trades)}")
    print(f"Total closed trades:  {total_trades}")
    print(f"Winning sessions:     {len(wins)}")
    print(f"Losing sessions:      {len(losses)}")
    print(f"Win rate:             {len(wins)/len(trades)*100:.1f}%")
    print(f"Total PnL:            {total_pnl:+.4f} USDT")
    print(f"Profit Factor:        {pf:.2f}")
    print(f"Avg PnL/session:      {total_pnl/len(trades):+.4f}")
    print()
    print("=" * 60)
    print("RECENT SESSIONS")
    print("=" * 60)
    for t in trades[-10:]:
        sign = "+" if t["pnl"] >= 0 else ""
        print(f"  {t['session'][:16]} | {t['count']:3d} trades | PnL {sign}{t['pnl']:.4f} | Return {sign}{t['return_pct']:.2f}%")

    print()
    print("=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    if pf >= 2.0:
        print("  PF >= 2.0: EXCELLENT - ready for capital")
    elif pf >= 1.5:
        print("  PF >= 1.5: STRONG - consider scaling")
    elif pf >= 1.2:
        print("  PF >= 1.2: ACCEPTABLE - keep optimizing")
    elif pf >= 1.0:
        print("  PF >= 1.0: MARGINAL - needs improvement")
    else:
        print("  PF < 1.0: LOSING - strategy change needed")


if __name__ == "__main__":
    analyze()
