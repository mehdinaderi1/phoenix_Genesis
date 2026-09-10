import pytest

from intelligence.action_proposal import ActionProposal
from execution.paper_trading_session import PaperTradingSession
from execution.paper_trading_cycle import PaperTradingCycle


def test_paper_trading_cycle_open_hold_close_open():

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    cycle = PaperTradingCycle(
        session
    )

    buy = ActionProposal(
        action="BUY",
        status="APPROVED",
        reason="Open BUY",
        confidence=80.0,
        symbol="BTCUSDT"
    )

    wait = ActionProposal(
        action="WAIT",
        status="REJECTED",
        reason="Wait",
        confidence=70.0,
        symbol="BTCUSDT"
    )

    sell = ActionProposal(
        action="SELL",
        status="APPROVED",
        reason="Close BUY",
        confidence=85.0,
        symbol="BTCUSDT"
    )

    # Cycle 1: OPEN BUY
    first = cycle.process(
        action_proposal=buy,
        price=100.0
    )

    assert first["action"] == "OPEN"
    assert first["position"] is not None
    assert first["position"].side == "BUY"
    assert first["position"].entry_price == 100.0

    # Cycle 2: HOLD
    second = cycle.process(
        action_proposal=wait,
        price=105.0
    )

    assert second["action"] == "HOLD"
    assert second["position"] is not None
    assert second["position"].side == "BUY"

    # Cycle 3: CLOSE BUY
    third = cycle.process(
        action_proposal=sell,
        price=110.0
    )

    assert third["action"] == "CLOSE"
    assert third["position"].side == "BUY"
    assert third["exit_price"] == 110.0
    assert third["realized_pnl"] == pytest.approx(10.0)

    # Position must be closed
    assert session.get_position() is None

    # Cycle 4: OPEN SELL
    fourth = cycle.process(
        action_proposal=sell,
        price=110.0
    )

    assert fourth["action"] == "OPEN"
    assert fourth["position"] is not None
    assert fourth["position"].side == "SELL"
    assert fourth["position"].entry_price == 110.0

    # Trade history contains exactly the completed BUY trade
    assert session.get_trade_count() == 1
    assert session.trade_history.get_total_realized_pnl() == pytest.approx(10.0)