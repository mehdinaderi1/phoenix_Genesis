"""
Risk integration tests with LiveExecutionAdapter.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from execution.live.live_execution_adapter import LiveExecutionAdapter
from risk.risk_state import RiskStateStore

POS = "data/_test_pos.json"
RISK = "data/_test_risk2.json"


def cleanup():
    for p in (POS, RISK):
        try: Path(p).unlink()
        except FileNotFoundError: pass


def t1_normal():
    print("=" * 60); print("1. Normal open + close with sizer"); print("=" * 60)
    cleanup()
    a = LiveExecutionAdapter(dry_run=True, state_path=POS, risk_state_path=RISK,
                             risk_config={"max_position_pct": 2.0, "risk_per_trade_pct": 0.5})
    print(f"  capital={a.risk_state.current_capital:.2f}")

    r = a.open_position("btc_usdt", "BUY", 80000, quantity=0.0001, sl=79000)
    print(f"  open: action={r['action']} qty={r.get('quantity')} sl={r.get('sl')}")
    assert r["action"] == "OPEN"
    assert r["quantity"] <= 0.00025

    r = a.close_position("btc_usdt", current_price=81000, reason="profit")
    print(f"  close: pnl={r['realized_pnl']:+.6f}")
    assert r["realized_pnl"] > 0

    st = RiskStateStore(RISK).load()
    print(f"  state: daily={st.daily_pnl:+.2f} total={st.total_trades}")
    assert st.total_trades == 1
    assert st.total_wins == 1
    print("  PASS")


def t2_daily_block():
    print(); print("=" * 60); print("2. Daily loss blocks"); print("=" * 60)
    cleanup()
    a = LiveExecutionAdapter(dry_run=True, state_path=POS, risk_state_path=RISK,
                             risk_config={"max_daily_loss_pct": 2.0})
    a.risk_state.record_trade(-25.0)
    a.save_risk_state()
    r = a.open_position("btc_usdt", "BUY", 80000, quantity=0.0001, sl=79000)
    print(f"  action={r['action']} reason={r.get('reason')}")
    assert r["action"] == "BLOCKED"
    assert "daily_loss" in r["reason"]
    print("  PASS")


def t3_kill_switch():
    print(); print("=" * 60); print("3. Kill switch"); print("=" * 60)
    cleanup()
    a = LiveExecutionAdapter(dry_run=True, state_path=POS, risk_state_path=RISK)
    a.kill_switch.trigger("manual", "test")
    r = a.open_position("btc_usdt", "BUY", 80000, quantity=0.0001, sl=79000)
    print(f"  blocked: reason={r.get('reason')}")
    assert r["action"] == "BLOCKED"

    a.kill_switch.release()
    r = a.open_position("btc_usdt", "BUY", 80000, quantity=0.0001, sl=79000)
    print(f"  after release: action={r['action']}")
    assert r["action"] == "OPEN"
    print("  PASS")


def t4_consec():
    print(); print("=" * 60); print("4. Consecutive losses"); print("=" * 60)
    cleanup()
    a = LiveExecutionAdapter(dry_run=True, state_path=POS, risk_state_path=RISK,
                             risk_config={"max_consecutive_losses": 3})
    for i in range(3):
        a.risk_state.record_trade(-1.0)
    a.save_risk_state()
    r = a.open_position("btc_usdt", "BUY", 80000, quantity=0.0001, sl=79000)
    print(f"  blocked: reason={r.get('reason')}")
    assert r["action"] == "BLOCKED"
    assert "consecutive" in r["reason"]
    print("  PASS")


def t5_persist():
    print(); print("=" * 60); print("5. Risk persistence across restart"); print("=" * 60)
    cleanup()
    a1 = LiveExecutionAdapter(dry_run=True, state_path=POS, risk_state_path=RISK)
    a1.open_position("btc_usdt", "BUY", 80000, quantity=0.0001, sl=79000)
    a1.close_position("btc_usdt", current_price=81000, reason="profit")
    cap1 = a1.risk_state.current_capital
    print(f"  a1 capital: {cap1:.2f}")

    a2 = LiveExecutionAdapter(dry_run=True, state_path=POS, risk_state_path=RISK)
    print(f"  a2 capital (restart): {a2.risk_state.current_capital:.2f}")
    assert abs(a2.risk_state.current_capital - cap1) < 1e-9
    assert a2.risk_state.total_trades == 1
    print("  PASS")


if __name__ == "__main__":
    t1_normal()
    t2_daily_block()
    t3_kill_switch()
    t4_consec()
    t5_persist()
    cleanup()
    print()
    print("=" * 60)
    print(">>> RISK INTEGRATION OK <<<")
    print("=" * 60)