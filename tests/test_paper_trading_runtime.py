import pytest

from intelligence.action_proposal import ActionProposal
from execution.paper_trading_session import PaperTradingSession
from execution.paper_trading_runtime import PaperTradingRuntime


def test_paper_trading_runtime_preserves_state_across_cycles():

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    runtime = PaperTradingRuntime(
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

    cycles = [
        {
            "action_proposal": buy,
            "price": 100.0
        },
        {
            "action_proposal": wait,
            "price": 105.0
        },
        {
            "action_proposal": sell,
            "price": 110.0
        }
    ]

    results = runtime.run(
        cycles=cycles
    )

    assert len(results) == 3

    assert results[0]["action"] == "OPEN"
    assert results[0]["position"] is not None
    assert results[0]["position"].side == "BUY"

    assert results[1]["action"] == "HOLD"
    assert results[1]["position"] is not None
    assert results[1]["position"].side == "BUY"

    assert results[2]["action"] == "CLOSE"
    assert results[2]["exit_price"] == 110.0
    assert results[2]["realized_pnl"] == pytest.approx(10.0)

    assert session.get_position() is None
    assert session.get_trade_count() == 1
    assert session.get_total_pnl() == pytest.approx(10.0)


def test_paper_trading_runtime_builds_summary():

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    runtime = PaperTradingRuntime(
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

    cycles = [
        {
            "action_proposal": buy,
            "price": 100.0
        },
        {
            "action_proposal": wait,
            "price": 105.0
        },
        {
            "action_proposal": sell,
            "price": 110.0
        }
    ]

    results = runtime.run(
        cycles=cycles
    )

    summary = runtime.build_summary(
        results
    )

    assert summary["cycles_processed"] == 3
    assert summary["open_count"] == 1
    assert summary["hold_count"] == 1
    assert summary["close_count"] == 1

    assert summary["current_position"] is None
    assert summary["balance"] == pytest.approx(1010.0)
    assert summary["total_pnl"] == pytest.approx(10.0)
    assert summary["trade_count"] == 1