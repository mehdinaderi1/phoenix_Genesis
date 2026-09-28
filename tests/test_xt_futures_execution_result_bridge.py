from execution.xt_futures_execution_result_bridge import (
    XTFuturesExecutionResultBridge,
)
from execution.xt_futures_order_confirmation import (
    XTFuturesOrderConfirmation,
    XTFuturesOrderConfirmationState,
)


def make_confirmed(quantity=0.001, price=67123.45):
    return XTFuturesOrderConfirmation(
        state=XTFuturesOrderConfirmationState.CONFIRMED,
        order_id="123",
        executed_quantity=quantity,
        average_price=price,
    )


def test_confirmed_fill_becomes_executed_result():
    confirmation = make_confirmed()

    result = XTFuturesExecutionResultBridge().build(
        confirmation=confirmation,
        action="BUY",
        symbol="BTCUSDT",
    )

    assert result is not None
    assert result.status == "EXECUTED"
    assert result.action == "BUY"
    assert result.symbol == "BTCUSDT"
    assert result.quantity == 0.001
    assert result.price == 67123.45


def test_confirmed_fill_preserves_sell_action():
    confirmation = make_confirmed()

    result = XTFuturesExecutionResultBridge().build(
        confirmation=confirmation,
        action="SELL",
        symbol="BTCUSDT",
    )

    assert result.status == "EXECUTED"
    assert result.action == "SELL"


def test_confirmed_without_quantity_does_not_execute():
    confirmation = make_confirmed(quantity=None)

    result = XTFuturesExecutionResultBridge().build(
        confirmation=confirmation,
        action="BUY",
        symbol="BTCUSDT",
    )

    assert result is None


def test_confirmed_without_price_does_not_execute():
    confirmation = make_confirmed(price=None)

    result = XTFuturesExecutionResultBridge().build(
        confirmation=confirmation,
        action="BUY",
        symbol="BTCUSDT",
    )

    assert result is None


def test_zero_quantity_does_not_execute():
    confirmation = make_confirmed(quantity=0)

    result = XTFuturesExecutionResultBridge().build(
        confirmation=confirmation,
        action="BUY",
        symbol="BTCUSDT",
    )

    assert result is None


def test_zero_price_does_not_execute():
    confirmation = make_confirmed(price=0)

    result = XTFuturesExecutionResultBridge().build(
        confirmation=confirmation,
        action="BUY",
        symbol="BTCUSDT",
    )

    assert result is None


def test_unknown_confirmation_does_not_execute():
    confirmation = XTFuturesOrderConfirmation(
        state=XTFuturesOrderConfirmationState.UNKNOWN,
        order_id="123",
        error="Order state: NEW",
        executed_quantity=0.001,
        average_price=67123.45,
    )

    result = XTFuturesExecutionResultBridge().build(
        confirmation=confirmation,
        action="BUY",
        symbol="BTCUSDT",
    )

    assert result is None


def test_rejected_confirmation_does_not_execute():
    confirmation = XTFuturesOrderConfirmation(
        state=XTFuturesOrderConfirmationState.REJECTED,
        order_id="123",
        error="Order state: REJECTED",
        executed_quantity=0.001,
        average_price=67123.45,
    )

    result = XTFuturesExecutionResultBridge().build(
        confirmation=confirmation,
        action="BUY",
        symbol="BTCUSDT",
    )

    assert result is None
