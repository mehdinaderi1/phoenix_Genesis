from execution.execution_result import ExecutionResult
from execution.paper_position_manager import PaperPositionManager


def test_none_quantity_does_not_open_position():
    manager = PaperPositionManager()

    execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=65000,
        quantity=None
    )

    position = manager.open_position(execution)

    assert position is None
    assert manager.get_position() is None


def test_zero_quantity_does_not_open_position():
    manager = PaperPositionManager()

    execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=65000,
        quantity=0
    )

    position = manager.open_position(execution)

    assert position is None
    assert manager.get_position() is None


def test_negative_quantity_does_not_open_position():
    manager = PaperPositionManager()

    execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=65000,
        quantity=-0.01
    )

    position = manager.open_position(execution)

    assert position is None
    assert manager.get_position() is None


def test_positive_quantity_opens_position():
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
    assert position.quantity == 0.01
    assert manager.get_position() is position