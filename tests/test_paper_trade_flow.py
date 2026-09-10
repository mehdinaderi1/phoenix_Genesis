from execution.paper_execution_engine import PaperExecutionEngine
from execution.paper_position_manager import PaperPositionManager
from execution.execution_result import ExecutionResult


def test_buy_paper_trade_end_to_end():

    execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=65000,
        quantity=0.01
    )

    execution_engine = PaperExecutionEngine()
    position_manager = PaperPositionManager()

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
    assert position.symbol == "BTCUSDT"
    assert position.side == "BUY"
    assert position.entry_price == 65000
    assert position.quantity == 0.01

    pnl = position_manager.calculate_pnl(
        66000
    )

    assert pnl == 10


def test_rejected_paper_trade_does_not_create_position():

    execution = ExecutionResult(
        status="NOT_EXECUTED",
        action="WAIT",
        symbol="BTCUSDT",
        price=65000
    )

    execution_engine = PaperExecutionEngine()
    position_manager = PaperPositionManager()

    result = execution_engine.execute(
        execution,
        price=65000,
        symbol="BTCUSDT"
    )

    assert result.status == "NOT_EXECUTED"

    position = position_manager.open_position(
        result
    )

    assert position is None
    assert position_manager.get_position() is None