from execution.xt_futures_order_request import XTFuturesOrderRequest


def test_open_long_request():
    request = XTFuturesOrderRequest(
        symbol="BTCUSDT",
        order_side="BUY",
        position_side="LONG",
        order_type="MARKET",
        quantity=0.001,
    )

    assert request.to_dict() == {
        "symbol": "BTCUSDT",
        "orderSide": "BUY",
        "positionSide": "LONG",
        "orderType": "MARKET",
        "origQty": 0.001,
    }


def test_close_long_request():
    request = XTFuturesOrderRequest(
        symbol="BTCUSDT",
        order_side="SELL",
        position_side="LONG",
        order_type="MARKET",
        quantity=0.001,
    )

    assert request.order_side == "SELL"
    assert request.position_side == "LONG"


def test_open_short_request():
    request = XTFuturesOrderRequest(
        symbol="BTCUSDT",
        order_side="SELL",
        position_side="SHORT",
        order_type="MARKET",
        quantity=0.001,
    )

    assert request.order_side == "SELL"
    assert request.position_side == "SHORT"


def test_close_short_request():
    request = XTFuturesOrderRequest(
        symbol="BTCUSDT",
        order_side="BUY",
        position_side="SHORT",
        order_type="MARKET",
        quantity=0.001,
    )

    assert request.order_side == "BUY"
    assert request.position_side == "SHORT"


def test_limit_order_serializes_price():
    request = XTFuturesOrderRequest(
        symbol="BTCUSDT",
        order_side="BUY",
        position_side="LONG",
        order_type="LIMIT",
        quantity=0.001,
        price=65000.0,
    )

    assert request.to_dict()["price"] == 65000.0


def test_wait_is_not_part_of_order_request_contract():
    request = XTFuturesOrderRequest(
        symbol="BTCUSDT",
        order_side="BUY",
        position_side="LONG",
        order_type="MARKET",
        quantity=0.001,
    )

    assert request.order_side in ("BUY", "SELL")


def test_invalid_order_side_is_rejected():
    try:
        XTFuturesOrderRequest(
            symbol="BTCUSDT",
            order_side="WAIT",
            position_side="LONG",
            order_type="MARKET",
            quantity=0.001,
        )
    except ValueError as exc:
        assert "order_side" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_invalid_quantity_is_rejected():
    try:
        XTFuturesOrderRequest(
            symbol="BTCUSDT",
            order_side="BUY",
            position_side="LONG",
            order_type="MARKET",
            quantity=0,
        )
    except ValueError as exc:
        assert "quantity" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_limit_order_requires_price():
    try:
        XTFuturesOrderRequest(
            symbol="BTCUSDT",
            order_side="BUY",
            position_side="LONG",
            order_type="LIMIT",
            quantity=0.001,
        )
    except ValueError as exc:
        assert "LIMIT" in str(exc)
    else:
        raise AssertionError("Expected ValueError")

