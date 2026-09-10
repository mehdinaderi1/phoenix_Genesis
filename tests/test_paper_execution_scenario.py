from intelligence.action_proposal import ActionProposal
import pytest
from execution.paper_execution_engine import PaperExecutionEngine
from execution.paper_position_manager import PaperPositionManager
from execution.paper_portfolio import PaperPortfolio
from execution.paper_trade_history import PaperTradeHistory


def test_approved_buy_full_paper_execution_scenario():

    action_proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        reason="Test approved BUY"
    )

    portfolio = PaperPortfolio.create(
        initial_balance=1000
    )

    trade_history = PaperTradeHistory()
    position_manager = PaperPositionManager()
    execution_engine = PaperExecutionEngine()

    entry_price = 65000

    execution_result = execution_engine.execute(
        action_proposal,
        price=entry_price,
        symbol="BTCUSDT",
        balance=portfolio.get_balance(),
        position_size_percent=1
    )

    assert execution_result.status == "EXECUTED"
    assert execution_result.action == "BUY"
    assert execution_result.symbol == "BTCUSDT"
    assert execution_result.quantity > 0

    expected_quantity = 10 / 65000

    assert execution_result.quantity == expected_quantity

    position = position_manager.open_position(
        execution_result
    )

    assert position is not None
    assert position.side == "BUY"
    assert position.entry_price == entry_price
    assert position.quantity == expected_quantity

    closed = position_manager.close_position_with_pnl(
        current_price=65100
    )

    assert closed is not None

    realized_pnl = closed["realized_pnl"]

    assert realized_pnl == pytest.approx(
        (65100 - 65000) * expected_quantity
    )

    portfolio.apply_realized_pnl(
        realized_pnl
    )

    trade = trade_history.add_trade(
        position=closed["position"],
        exit_price=closed["exit_price"],
        realized_pnl=closed["realized_pnl"]
    )

    assert trade is not None

    assert portfolio.get_total_pnl() == pytest.approx(
        realized_pnl
    )

    assert portfolio.get_balance() == pytest.approx(
        1000 + realized_pnl
    )

    assert trade_history.get_trade_count() == 1

    assert trade_history.get_total_realized_pnl() == (
        realized_pnl
    )

    assert position_manager.get_position() is None