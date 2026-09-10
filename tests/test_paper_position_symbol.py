from execution.execution_result import ExecutionResult
from execution.paper_position_manager import PaperPositionManager


def test_none_symbol_does_not_open_position():
    manager = PaperPositionManager()

    execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol=None,
        price=65000,
        quantity=0.01
    )

    position = manager.open_position(execution)

    assert position is None
    assert manager.get_position() is None


def test_empty_symbol_does_not_open_position():
    manager = PaperPositionManager()

    execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="",
        price=65000,
        quantity=0.01
    )

    position = manager.open_position(execution)

    assert position is None
    assert manager.get_position() is None


def test_valid_symbol_opens_position():
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
    assert position.symbol == "BTCUSDT"
    assert manager.get_position() is position