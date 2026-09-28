from execution.execution_result import ExecutionResult
from execution.paper_trading_session import PaperTradingSession
from execution.xt_futures_position_close_bridge import (
    XTFuturesPositionCloseBridge,
)
from intelligence.action_proposal import ActionProposal


def make_execution_result(
    action="SELL",
    symbol="BTCUSDT",
    price=68000.0,
    quantity=0.001,
):
    return ExecutionResult(
        status="EXECUTED",
        action=action,
        symbol=symbol,
        price=price,
        quantity=quantity,
    )


def open_long(session):
    proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        reason="Open LONG",
        confidence=90.0,
        symbol="BTCUSDT",
    )

    result = session.process_action(
        action_proposal=proposal,
        price=67000.0,
        symbol="BTCUSDT",
    )

    assert result["position"] is not None
    assert result["position"].side == "BUY"


def test_confirmed_sell_closes_existing_long():
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0,
    )

    open_long(session)

    position = session.get_position()
    expected_pnl = (
        68000.0 - position.entry_price
    ) * position.quantity

    bridge = XTFuturesPositionCloseBridge(
        session=session
    )

    result = bridge.apply(
        make_execution_result(
            action="SELL",
            price=68000.0,
        )
    )

    assert result is not None
    assert result["position"].side == "BUY"
    assert result["exit_price"] == 68000.0
    assert result["realized_pnl"] == expected_pnl

    assert session.get_position() is None
    assert session.get_trade_count() == 1
    assert session.get_balance() == 1000.0 + expected_pnl


def test_confirmed_buy_closes_existing_short():
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0,
    )

    proposal = ActionProposal(
        action="SELL",
        status="APPROVED",
        reason="Open SHORT",
        confidence=90.0,
        symbol="BTCUSDT",
    )

    result = session.process_action(
        action_proposal=proposal,
        price=68000.0,
        symbol="BTCUSDT",
    )

    assert result["position"] is not None
    assert result["position"].side == "SELL"

    position = session.get_position()
    expected_pnl = (
        position.entry_price - 67000.0
    ) * position.quantity

    bridge = XTFuturesPositionCloseBridge(
        session=session
    )

    result = bridge.apply(
        make_execution_result(
            action="BUY",
            price=67000.0,
        )
    )

    assert result is not None
    assert result["position"].side == "SELL"
    assert result["exit_price"] == 67000.0
    assert result["realized_pnl"] == expected_pnl

    assert session.get_position() is None
    assert session.get_trade_count() == 1
    assert session.get_balance() == 1000.0 + expected_pnl


def test_same_direction_execution_does_not_close_position():
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0,
    )

    open_long(session)

    bridge = XTFuturesPositionCloseBridge(
        session=session
    )

    result = bridge.apply(
        make_execution_result(
            action="BUY",
            price=68000.0,
        )
    )

    assert result is None
    assert session.get_position() is not None
    assert session.get_position().side == "BUY"
    assert session.get_trade_count() == 0


def test_unknown_execution_does_not_close_position():
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0,
    )

    open_long(session)

    bridge = XTFuturesPositionCloseBridge(
        session=session
    )

    execution = ExecutionResult(
        status="UNKNOWN",
        action="SELL",
        symbol="BTCUSDT",
        price=68000.0,
        quantity=0.001,
    )

    result = bridge.apply(execution)

    assert result is None
    assert session.get_position() is not None
    assert session.get_trade_count() == 0
