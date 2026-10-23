"""
Integration test for risk management.
No exchange calls — pure logic.
"""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from risk.risk_state import RiskState, RiskStateStore
from risk.position_sizer import PositionSizer
from risk.risk_guard import RiskGuard
from risk.kill_switch import KillSwitch

STATE = "data/_test_risk.json"


def cleanup():
    p = Path(STATE)
    if p.exists():
        p.unlink()


def test_sizer():
    print("=" * 60)
    print("1. PositionSizer")
    print("=" * 60)

    sizer = PositionSizer(risk_per_trade_pct=0.5, max_position_pct=2.0)

    # capital=1000, entry=80000, sl=79000 (distance=1000)
    # risk_amount = 1000 * 0.5/100 = $5
    # raw_qty = 5 / 1000 = 0.005
    # max_qty = 1000 * 2/100 / 80000 = 0.00025
    # capped = 0.00025
    r = sizer.compute(capital=1000, entry_price=80000, stop_loss=79000)
    print(f"  capital=1000, entry=80000, sl=79000:")
    print(f"    allowed={r.allowed} qty={r.quantity} notional=${r.notional} reason={r.reason}")
    assert r.allowed
    assert r.quantity == 0.00025, f"expected 0.00025, got {r.quantity}"

    # tight SL: distance=100 → raw_qty=0.05, capped by max=0.00025
    r = sizer.compute(capital=1000, entry_price=80000, stop_loss=79900)
    print(f"  tight SL 79900:")
    print(f"    allowed={r.allowed} qty={r.quantity} reason={r.reason}")
    assert r.quantity <= 0.00025

    # huge SL: distance=50000 → raw_qty=0.0001, not capped
    r = sizer.compute(capital=1000, entry_price=80000, stop_loss=30000)
    print(f"  huge SL 30000:")
    print(f"    allowed={r.allowed} qty={r.quantity} reason={r.reason}")
    assert r.allowed
    assert r.reason == "ok"

    # zero sl distance
    r = sizer.compute(capital=1000, entry_price=80000, stop_loss=80000)
    print(f"  zero SL:")
    print(f"    allowed={r.allowed} reason={r.reason}")
    assert not r.allowed

    print("  PASS")


def test_guard():
    print()
    print("=" * 60)
    print("2. RiskGuard")
    print("=" * 60)

    guard = RiskGuard()
    state = RiskState(initial_capital=1000, current_capital=1000, peak_capital=1000)

    # Clean
    d = guard.check(state, current_position_count=0)
    print(f"  clean state: allowed={d.allowed} reason={d.reason}")
    assert d.allowed

    # 1 position open
    d = guard.check(state, current_position_count=1)
    print(f"  1 position: allowed={d.allowed} reason={d.reason}")
    assert not d.allowed

    # Daily loss
    state.record_trade(-15.0)  # -1.5%
    d = guard.check(state, current_position_count=0)
    print(f"  -1.5% daily: allowed={d.allowed} reason={d.reason}")
    assert d.allowed

    state.record_trade(-10.0)  # -2.5% total
    d = guard.check(state, current_position_count=0)
    print(f"  -2.5% daily: allowed={d.allowed} reason={d.reason}")
    assert not d.allowed

    print("  PASS")


def test_kill_switch():
    print()
    print("=" * 60)
    print("3. KillSwitch")
    print("=" * 60)

    cleanup()
    store = RiskStateStore(STATE)
    ks = KillSwitch(store)

    print(f"  initially active: {ks.is_active()}")
    assert not ks.is_active()

    ks.trigger("manual", "operator requested")
    print(f"  after trigger: {ks.is_active()}")
    assert ks.is_active()

    # Guard should refuse
    guard = RiskGuard()
    state = store.load()
    d = guard.check(state, current_position_count=0)
    print(f"  guard with KS: allowed={d.allowed} reason={d.reason}")
    assert not d.allowed
    assert "kill_switch" in d.reason

    ks.release()
    print(f"  after release: {ks.is_active()}")
    assert not ks.is_active()

    print("  PASS")


def test_consecutive_losses():
    print()
    print("=" * 60)
    print("4. Consecutive losses")
    print("=" * 60)

    guard = RiskGuard(max_consecutive_losses=3)
    state = RiskState(initial_capital=1000, current_capital=1000, peak_capital=1000)

    for i in range(3):
        state.record_trade(-1.0)
        d = guard.check(state, current_position_count=0)
        print(f"  after loss {i+1}: allowed={d.allowed} reason={d.reason}")

    # 3rd loss should block
    assert state.consecutive_losses == 3
    d = guard.check(state, current_position_count=0)
    assert not d.allowed
    assert "consecutive_losses" in d.reason

    print("  PASS")


def test_persistence():
    print()
    print("=" * 60)
    print("5. RiskState persistence")
    print("=" * 60)

    cleanup()
    store = RiskStateStore(STATE)
    state = RiskState(initial_capital=1000, current_capital=1000)
    state.record_trade(+5.0)
    state.record_trade(-2.0)
    store.save(state)

    print(f"  saved to {STATE}")

    loaded = store.load()
    print(f"  loaded capital: {loaded.current_capital}")
    print(f"  loaded daily_pnl: {loaded.daily_pnl}")
    assert loaded.current_capital == 1003.0
    assert loaded.daily_pnl == 3.0
    assert loaded.total_trades == 2
    assert loaded.total_wins == 1
    assert loaded.total_losses == 1

    cleanup()
    print("  PASS")


def main():
    test_sizer()
    test_guard()
    test_kill_switch()
    test_consecutive_losses()
    test_persistence()
    print()
    print("=" * 60)
    print(">>> ALL RISK TESTS PASS <<<")
    print("=" * 60)


if __name__ == "__main__":
    main()