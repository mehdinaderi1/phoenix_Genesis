from execution.execution_result import ExecutionResult
from execution.paper_position_manager import PaperPositionManager


def test_none_price_does_not_open_position():
    manager = PaperPositionManager()

    execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=None,
        quantity=0.01
    )

    position = manager.open_position(execution)

    assert position is None
    assert manager.get_position() is None


def test_zero_price_does_not_open_position():
    manager = PaperPositionManager()

    execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=0,
        quantity=0.01
    )

    position = manager.open_position(execution)

    assert position is None
    assert manager.get_position() is None


def test_negative_price_does_not_open_position():
    manager = PaperPositionManager()

    execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=-65000,
        quantity=0.01
    )

    position = manager.open_position(execution)

    assert position is None
    assert manager.get_position() is None


def test_positive_price_opens_position():
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
    assert position.entry_price == 65000
    assert manager.get_position() is position