from execution.execution_result import ExecutionResult
from execution.paper_position_manager import PaperPositionManager
from execution.xt_futures_position_bridge import (
    XTFuturesPositionBridge,
)


def make_execution_result(
    status="EXECUTED",
    action="BUY",
    symbol="BTCUSDT",
    price=67123.45,
    quantity=0.001,
):
    return ExecutionResult(
        status=status,
        action=action,
        symbol=symbol,
        price=price,
        quantity=quantity,
    )


def test_executed_result_creates_position():
    manager = PaperPositionManager()
    bridge = XTFuturesPositionBridge(
        position_manager=manager
    )

    result = bridge.apply(
        make_execution_result()
    )

    assert result is not None
    assert result.symbol == "BTCUSDT"
    assert result.side == "BUY"
    assert result.entry_price == 67123.45
    assert result.quantity == 0.001

    assert manager.get_position() is result


def test_executed_sell_result_creates_short_position():
    manager = PaperPositionManager()
    bridge = XTFuturesPositionBridge(
        position_manager=manager
    )

    result = bridge.apply(
        make_execution_result(
            action="SELL"
        )
    )

    assert result is not None
    assert result.side == "SELL"


def test_sent_result_does_not_create_position():
    manager = PaperPositionManager()
    bridge = XTFuturesPositionBridge(
        position_manager=manager
    )

    result = bridge.apply(
        make_execution_result(
            status="SENT"
        )
    )

    assert result is None
    assert manager.get_position() is None


def test_unknown_result_does_not_create_position():
    manager = PaperPositionManager()
    bridge = XTFuturesPositionBridge(
        position_manager=manager
    )

    result = bridge.apply(
        make_execution_result(
            status="UNKNOWN"
        )
    )

    assert result is None
    assert manager.get_position() is None


def test_rejected_result_does_not_create_position():
    manager = PaperPositionManager()
    bridge = XTFuturesPositionBridge(
        position_manager=manager
    )

    result = bridge.apply(
        make_execution_result(
            status="REJECTED"
        )
    )

    assert result is None
    assert manager.get_position() is None


def test_invalid_quantity_does_not_create_position():
    manager = PaperPositionManager()
    bridge = XTFuturesPositionBridge(
        position_manager=manager
    )

    result = bridge.apply(
        make_execution_result(
            quantity=0
        )
    )

    assert result is None
    assert manager.get_position() is None


def test_invalid_price_does_not_create_position():
    manager = PaperPositionManager()
    bridge = XTFuturesPositionBridge(
        position_manager=manager
    )

    result = bridge.apply(
        make_execution_result(
            price=0
        )
    )

    assert result is None
    assert manager.get_position() is None


def test_existing_position_is_not_replaced():
    manager = PaperPositionManager()
    bridge = XTFuturesPositionBridge(
        position_manager=manager
    )

    first = bridge.apply(
        make_execution_result(
            action="BUY",
            price=67000.0,
        )
    )

    second = bridge.apply(
        make_execution_result(
            action="SELL",
            price=68000.0,
        )
    )

    assert first is not None
    assert second is None
    assert manager.get_position() is first
