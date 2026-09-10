from execution.paper_position import PaperPosition
from execution.paper_position_manager import PaperPositionManager
from execution.paper_portfolio import PaperPortfolio
from execution.paper_trade_history import PaperTradeHistory
from execution.execution_result import ExecutionResult


def test_closed_trade_updates_portfolio_and_history():

    execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=65000,
        quantity=0.01
    )

    position_manager = PaperPositionManager()
    portfolio = PaperPortfolio.create(
        initial_balance=1000
    )
    history = PaperTradeHistory()

    position = position_manager.open_position(
        execution
    )

    assert position is not None

    closed = position_manager.close_position_with_pnl(
        current_price=66000
    )

    assert closed is not None
    assert closed["realized_pnl"] == 10

    portfolio.apply_realized_pnl(
        closed["realized_pnl"]
    )

    record = history.add_trade(
        position=closed["position"],
        exit_price=closed["exit_price"],
        realized_pnl=closed["realized_pnl"]
    )

    assert portfolio.get_balance() == 1010
    assert portfolio.get_total_pnl() == 10

    assert history.get_trade_count() == 1
    assert history.get_total_realized_pnl() == 10

    assert record.symbol == "BTCUSDT"
    assert record.entry_price == 65000
    assert record.exit_price == 66000
    assert record.realized_pnl == 10


def test_multiple_closed_trades_update_portfolio_and_history():

    position_manager = PaperPositionManager()
    portfolio = PaperPortfolio.create(
        initial_balance=1000
    )
    history = PaperTradeHistory()

    first_execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=65000,
        quantity=0.01
    )

    position = position_manager.open_position(
        first_execution
    )

    closed = position_manager.close_position_with_pnl(
        current_price=66000
    )

    portfolio.apply_realized_pnl(
        closed["realized_pnl"]
    )

    history.add_trade(
        position=closed["position"],
        exit_price=closed["exit_price"],
        realized_pnl=closed["realized_pnl"]
    )

    second_execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=66000,
        quantity=0.01
    )

    position = position_manager.open_position(
        second_execution
    )

    closed = position_manager.close_position_with_pnl(
        current_price=65500
    )

    portfolio.apply_realized_pnl(
        closed["realized_pnl"]
    )

    history.add_trade(
        position=closed["position"],
        exit_price=closed["exit_price"],
        realized_pnl=closed["realized_pnl"]
    )

    assert history.get_trade_count() == 2
    assert history.get_total_realized_pnl() == 5

    assert portfolio.get_balance() == 1005
    assert portfolio.get_total_pnl() == 5