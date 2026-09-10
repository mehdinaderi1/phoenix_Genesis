from execution.execution_result import ExecutionResult
from execution.paper_position_manager import PaperPositionManager


def test_buy_position_profit():
    manager = PaperPositionManager()

    execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=65000,
        quantity=0.01
    )

    position = manager.open_position(execution)

    assert position is not None
    assert position.side == "BUY"
    assert manager.calculate_pnl(66000) == 10


def test_buy_position_loss():
    manager = PaperPositionManager()

    execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=65000,
        quantity=0.01
    )

    manager.open_position(execution)

    assert manager.calculate_pnl(64000) == -10


def test_sell_position_profit():
    manager = PaperPositionManager()

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
    assert manager.calculate_pnl(64000) == 10


def test_sell_position_loss():
    manager = PaperPositionManager()

    execution = ExecutionResult(
        status="EXECUTED",
        action="SELL",
        symbol="BTCUSDT",
        price=65000,
        quantity=0.01
    )

    manager.open_position(execution)

    assert manager.calculate_pnl(66000) == -10