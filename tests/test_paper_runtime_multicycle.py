import pytest

from intelligence.action_proposal import ActionProposal
from execution.paper_trading_session import PaperTradingSession


def test_paper_runtime_stateful_multi_cycle():

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    # Cycle 1: BUY
    buy_proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        reason="Cycle 1 BUY",
        confidence=80.0,
        symbol="BTCUSDT",
        strategy="test_strategy",
        risk_status="LOW"
    )

    result = session.process_action(
        action_proposal=buy_proposal,
        price=100.0,
        symbol="BTCUSDT"
    )

    assert result["execution_result"].status == "EXECUTED"
    assert result["position"] is not None
    assert result["position"].side == "BUY"

    # Position must remain open during the cycle
    assert session.get_position() is not None
    assert session.get_trade_count() == 0

    # Close Cycle 1
    closed = session.close_position(
        exit_price=110.0
    )

    assert closed is not None
    assert closed["realized_pnl"] == pytest.approx(10.0)

    assert session.get_position() is None
    assert session.get_balance() == pytest.approx(1010.0)
    assert session.get_total_pnl() == pytest.approx(10.0)
    assert session.get_trade_count() == 1

    # Cycle 2: SELL using updated portfolio state
    sell_proposal = ActionProposal(
        action="SELL",
        status="APPROVED",
        reason="Cycle 2 SELL",
        confidence=80.0,
        symbol="BTCUSDT",
        strategy="test_strategy",
        risk_status="LOW"
    )

    result = session.process_action(
        action_proposal=sell_proposal,
        price=100.0,
        symbol="BTCUSDT"
    )

    assert result["execution_result"].status == "EXECUTED"
    assert result["position"] is not None
    assert result["position"].side == "SELL"

    # Updated balance must affect position sizing
    assert result["position"].quantity == pytest.approx(1.01)

    # Close Cycle 2
    closed = session.close_position(
        exit_price=90.0
    )

    assert closed is not None
    assert closed["realized_pnl"] == pytest.approx(10.1)

    # Final state after multiple runtime cycles
    assert session.get_position() is None
    assert session.get_balance() == pytest.approx(1020.1)
    assert session.get_total_pnl() == pytest.approx(20.1)
    assert session.get_trade_count() == 2

    assert (
        session.trade_history.get_total_realized_pnl()
        == pytest.approx(20.1)
    )