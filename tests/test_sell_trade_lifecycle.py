from execution.execution_result import ExecutionResult
from execution.paper_position_manager import PaperPositionManager
from execution.paper_portfolio import PaperPortfolio
from execution.paper_trade_history import PaperTradeHistory


def test_sell_trade_lifecycle_with_profit():
    manager = PaperPositionManager()
    portfolio = PaperPortfolio.create(initial_balance=1000)
    history = PaperTradeHistory()

    execution = ExecutionResult(
        status="EXECUTED",
        action="SELL",
        symbol="BTCUSDT",
        price=65000,
        quantity=0.01
    )

    position = manager.open_position(execution)

    assert position is not None
    assert position.side == "SELL"

    closed = manager.close_position_with_pnl(
        current_price=64000
    )

    assert closed is not None
    assert closed["realized_pnl"] == 10

    portfolio.apply_realized_pnl(
        closed["realized_pnl"]
    )

    trade = history.add_trade(
        position=closed["position"],
        exit_price=closed["exit_price"],
        realized_pnl=closed["realized_pnl"]
    )

    assert trade.side == "SELL"
    assert trade.entry_price == 65000
    assert trade.exit_price == 64000
    assert trade.realized_pnl == 10

    assert portfolio.get_balance() == 1010
    assert history.get_trade_count() == 1
    assert history.get_total_realized_pnl() == 10
    assert manager.get_position() is None


def test_sell_trade_lifecycle_with_loss():
    manager = PaperPositionManager()
    portfolio = PaperPortfolio.create(initial_balance=1000)
    history = PaperTradeHistory()

    execution = ExecutionResult(
        status="EXECUTED",
        action="SELL",
        symbol="BTCUSDT",
        price=65000,
        quantity=0.01
    )

    position = manager.open_position(execution)

    assert position is not None
    assert position.side == "SELL"

    closed = manager.close_position_with_pnl(
        current_price=66000
    )

    assert closed is not None
    assert closed["realized_pnl"] == -10

    portfolio.apply_realized_pnl(
        closed["realized_pnl"]
    )

    history.add_trade(
        position=closed["position"],
        exit_price=closed["exit_price"],
        realized_pnl=closed["realized_pnl"]
    )

    assert portfolio.get_balance() == 990
    assert history.get_trade_count() == 1
    assert history.get_total_realized_pnl() == -10
    assert manager.get_position() is None