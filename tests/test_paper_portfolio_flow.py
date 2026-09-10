from execution.paper_execution_engine import PaperExecutionEngine
from execution.paper_position_manager import PaperPositionManager
from execution.paper_portfolio import PaperPortfolio
from execution.execution_result import ExecutionResult


def test_paper_trade_updates_portfolio_after_realized_pnl():

    execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=65000,
        quantity=0.01
    )

    execution_engine = PaperExecutionEngine()
    position_manager = PaperPositionManager()
    portfolio = PaperPortfolio.create(
        initial_balance=1000
    )

    result = execution_engine.execute(
        execution,
        price=65000,
        symbol="BTCUSDT",
        quantity=0.01
    )

    assert result.status == "EXECUTED"

    position = position_manager.open_position(
        result
    )

    assert position is not None

    closed = position_manager.close_position_with_pnl(
        current_price=66000
    )

    assert closed is not None
    assert closed["realized_pnl"] == 10

    balance = portfolio.apply_realized_pnl(
        closed["realized_pnl"]
    )

    assert balance == 1010
    assert portfolio.get_balance() == 1010
    assert portfolio.get_total_pnl() == 10


def test_losing_paper_trade_updates_portfolio():

    execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=65000,
        quantity=0.01
    )

    execution_engine = PaperExecutionEngine()
    position_manager = PaperPositionManager()
    portfolio = PaperPortfolio.create(
        initial_balance=1000
    )

    result = execution_engine.execute(
        execution,
        price=65000,
        symbol="BTCUSDT",
        quantity=0.01
    )

    position_manager.open_position(result)

    closed = position_manager.close_position_with_pnl(
        current_price=64000
    )

    assert closed["realized_pnl"] == -10

    balance = portfolio.apply_realized_pnl(
        closed["realized_pnl"]
    )

    assert balance == 990
    assert portfolio.get_total_pnl() == -10