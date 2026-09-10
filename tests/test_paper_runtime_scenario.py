import pytest

from intelligence.action_proposal import ActionProposal
from execution.paper_trading_session import PaperTradingSession


def test_paper_runtime_buy_and_sell_cycles():

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    # ---------------------------------------------------------
    # BUY Cycle
    # ---------------------------------------------------------

    buy_proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        reason="BUY runtime scenario",
        confidence=80.0,
        symbol="BTCUSDT",
        strategy="test_strategy",
        risk_status="LOW"
    )

    buy_result = session.process_action(
        action_proposal=buy_proposal,
        price=100.0,
        symbol="BTCUSDT"
    )

    assert buy_result["execution_result"].status == "EXECUTED"
    assert buy_result["execution_result"].action == "BUY"
    assert buy_result["position"] is not None
    assert buy_result["position"].side == "BUY"

    buy_closed = session.close_position(
        exit_price=110.0
    )

    assert buy_closed is not None
    assert buy_closed["realized_pnl"] == pytest.approx(10.0)

    assert session.get_position() is None
    assert session.get_balance() == pytest.approx(1010.0)
    assert session.get_total_pnl() == pytest.approx(10.0)
    assert session.get_trade_count() == 1

    # ---------------------------------------------------------
    # SELL Cycle
    # ---------------------------------------------------------

    sell_proposal = ActionProposal(
        action="SELL",
        status="APPROVED",
        reason="SELL runtime scenario",
        confidence=80.0,
        symbol="BTCUSDT",
        strategy="test_strategy",
        risk_status="LOW"
    )

    sell_result = session.process_action(
        action_proposal=sell_proposal,
        price=100.0,
        symbol="BTCUSDT"
    )

    assert sell_result["execution_result"].status == "EXECUTED"
    assert sell_result["execution_result"].action == "SELL"
    assert sell_result["position"] is not None
    assert sell_result["position"].side == "SELL"

    sell_closed = session.close_position(
        exit_price=90.0
    )

    assert sell_closed is not None
    assert sell_closed["realized_pnl"] == pytest.approx(10.1)

    # ---------------------------------------------------------
    # Final State
    # ---------------------------------------------------------

    assert session.get_position() is None
    assert session.get_balance() == pytest.approx(1020.1)
    assert session.get_total_pnl() == pytest.approx(20.1)
    assert session.get_trade_count() == 2

    assert (
        session.trade_history.get_total_realized_pnl()
        == pytest.approx(20.1)
    )