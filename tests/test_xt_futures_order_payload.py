import pytest

from execution.xt_futures_order_payload import (
    XTFuturesOrderPayloadBuilder
)
from execution.xt_futures_order_request import (
    XTFuturesOrderRequest
)


@pytest.fixture
def builder():
    return XTFuturesOrderPayloadBuilder()


def test_open_long_market_payload(builder):
    request = XTFuturesOrderRequest(
        symbol="BTCUSDT",
        order_side="BUY",
        position_side="LONG",
        order_type="MARKET",
        quantity=0.001
    )

    payload = builder.build(request)

    assert payload == {
        "symbol": "BTCUSDT",
        "orderSide": "BUY",
        "positionSide": "LONG",
        "orderType": "MARKET",
        "origQty": 0.001,
    }


def test_open_short_market_payload(builder):
    request = XTFuturesOrderRequest(
        symbol="BTCUSDT",
        order_side="SELL",
        position_side="SHORT",
        order_type="MARKET",
        quantity=0.001
    )

    payload = builder.build(request)

    assert payload["orderSide"] == "SELL"
    assert payload["positionSide"] == "SHORT"


def test_close_long_market_payload(builder):
    request = XTFuturesOrderRequest(
        symbol="BTCUSDT",
        order_side="SELL",
        position_side="LONG",
        order_type="MARKET",
        quantity=0.001
    )

    payload = builder.build(request)

    assert payload["orderSide"] == "SELL"
    assert payload["positionSide"] == "LONG"


def test_close_short_market_payload(builder):
    request = XTFuturesOrderRequest(
        symbol="BTCUSDT",
        order_side="BUY",
        position_side="SHORT",
        order_type="MARKET",
        quantity=0.001
    )

    payload = builder.build(request)

    assert payload["orderSide"] == "BUY"
    assert payload["positionSide"] == "SHORT"


def test_limit_payload_contains_price(builder):
    request = XTFuturesOrderRequest(
        symbol="BTCUSDT",
        order_side="BUY",
        position_side="LONG",
        order_type="LIMIT",
        quantity=0.001,
        price=65000.0
    )

    payload = builder.build(request)

    assert payload["orderType"] == "LIMIT"
    assert payload["price"] == 65000.0


def test_market_payload_does_not_add_price(builder):
    request = XTFuturesOrderRequest(
        symbol="BTCUSDT",
        order_side="BUY",
        position_side="LONG",
        order_type="MARKET",
        quantity=0.001
    )

    payload = builder.build(request)

    assert "price" not in payload


def test_builder_rejects_invalid_request(builder):
    with pytest.raises(
        TypeError,
        match="request must be XTFuturesOrderRequest"
    ):
        builder.build({"symbol": "BTCUSDT"})
