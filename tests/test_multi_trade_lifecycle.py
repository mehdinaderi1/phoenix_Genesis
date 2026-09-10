from execution.execution_result import ExecutionResult
from execution.paper_position_manager import PaperPositionManager
from execution.paper_portfolio import PaperPortfolio
from execution.paper_trade_history import PaperTradeHistory


def test_multiple_trades_lifecycle():

    manager = PaperPositionManager()
    portfolio = PaperPortfolio.create(initial_balance=1000)
    history = PaperTradeHistory()

    # Trade #1
    first_execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=65000,
        quantity=0.01
    )

    first_position = manager.open_position(first_execution)

    assert first_position is not None
    assert first_position.entry_price == 65000

    first_closed = manager.close_position_with_pnl(
        current_price=66000
    )

    assert first_closed is not None
    assert first_closed["realized_pnl"] == 10

    portfolio.apply_realized_pnl(
        first_closed["realized_pnl"]
    )

    history.add_trade(
        position=first_closed["position"],
        exit_price=first_closed["exit_price"],
        realized_pnl=first_closed["realized_pnl"]
    )

    assert manager.get_position() is None
    assert portfolio.get_balance() == 1010
    assert history.get_trade_count() == 1

    # Trade #2
    second_execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=66000,
        quantity=0.01
    )

    second_position = manager.open_position(second_execution)

    assert second_position is not None
    assert second_position.entry_price == 66000

    second_closed = manager.close_position_with_pnl(
        current_price=65000
    )

    assert second_closed is not None
    assert second_closed["realized_pnl"] == -10

    portfolio.apply_realized_pnl(
        second_closed["realized_pnl"]
    )

    history.add_trade(
        position=second_closed["position"],
        exit_price=second_closed["exit_price"],
        realized_pnl=second_closed["realized_pnl"]
    )

    assert manager.get_position() is None
    assert portfolio.get_balance() == 1000
    assert history.get_trade_count() == 2
    assert history.get_total_realized_pnl() == 0