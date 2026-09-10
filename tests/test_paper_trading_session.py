import pytest

from intelligence.action_proposal import ActionProposal
from execution.paper_trading_session import PaperTradingSession


def test_paper_trading_session_buy_and_close_profit():
    proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        reason="Valid BUY setup",
        confidence=80.0,
        symbol="BTCUSDT",
        strategy="test_strategy",
        risk_status="LOW"
    )

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    result = session.process_action(
        action_proposal=proposal,
        price=100.0,
        symbol="BTCUSDT"
    )

    execution = result["execution_result"]
    position = result["position"]

    assert execution.status == "EXECUTED"
    assert execution.action == "BUY"
    assert execution.symbol == "BTCUSDT"
    assert execution.price == 100.0
    assert execution.quantity == pytest.approx(1.0)

    assert position is not None
    assert position.side == "BUY"
    assert position.entry_price == 100.0
    assert position.quantity == pytest.approx(1.0)

    closed = session.close_position(
        exit_price=110.0
    )

    assert closed is not None
    assert closed["realized_pnl"] == pytest.approx(10.0)

    assert session.get_position() is None
    assert session.get_balance() == pytest.approx(1010.0)
    assert session.get_total_pnl() == pytest.approx(10.0)
    assert session.get_trade_count() == 1


def test_paper_trading_session_sell_and_close_profit():
    proposal = ActionProposal(
        action="SELL",
        status="APPROVED",
        reason="Valid SELL setup",
        confidence=80.0,
        symbol="BTCUSDT",
        strategy="test_strategy",
        risk_status="LOW"
    )

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    result = session.process_action(
        action_proposal=proposal,
        price=100.0,
        symbol="BTCUSDT"
    )

    execution = result["execution_result"]
    position = result["position"]

    assert execution.status == "EXECUTED"
    assert execution.action == "SELL"
    assert execution.quantity == pytest.approx(1.0)

    assert position is not None
    assert position.side == "SELL"
    assert position.entry_price == 100.0
    assert position.quantity == pytest.approx(1.0)

    closed = session.close_position(
        exit_price=90.0
    )

    assert closed is not None
    assert closed["realized_pnl"] == pytest.approx(10.0)

    assert session.get_position() is None
    assert session.get_balance() == pytest.approx(1010.0)
    assert session.get_total_pnl() == pytest.approx(10.0)
    assert session.get_trade_count() == 1


def test_paper_trading_session_wait_does_not_open_position():
    proposal = ActionProposal(
        action="WAIT",
        status="REJECTED",
        reason="Market conditions require monitoring",
        confidence=70.0,
        symbol="BTCUSDT",
        risk_status="MEDIUM"
    )

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    result = session.process_action(
        action_proposal=proposal,
        price=65000.0,
        symbol="BTCUSDT"
    )

    execution = result["execution_result"]

    assert execution.status == "NOT_EXECUTED"
    assert execution.action == "WAIT"

    assert result["position"] is None

    assert session.get_position() is None
    assert session.get_balance() == pytest.approx(1000.0)
    assert session.get_total_pnl() == pytest.approx(0.0)
    assert session.get_trade_count() == 0


def test_paper_trading_session_no_position_close():
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    closed = session.close_position(
        exit_price=110.0
    )

    assert closed is None

    assert session.get_position() is None
    assert session.get_balance() == pytest.approx(1000.0)
    assert session.get_total_pnl() == pytest.approx(0.0)
    assert session.get_trade_count() == 0
