from execution.xt_futures_order_request import XTFuturesOrderRequest
from execution.xt_futures_transport_request_builder import (
    XTFuturesTransportRequestBuilder,
)


def make_order_request():
    return XTFuturesOrderRequest(
        symbol="BTCUSDT",
        order_side="BUY",
        position_side="LONG",
        order_type="MARKET",
        quantity=0.001,
    )


def test_builder_creates_authenticated_transport_request():
    builder = XTFuturesTransportRequestBuilder(
        appkey="APPKEY",
        secret_key="SECRET",
    )

    result = builder.build(
        request=make_order_request(),
        timestamp="1234567890",
    )

    assert result.endpoint == (
        "/future/trade/v1/order/create"
    )
    assert result.timestamp == "1234567890"
    assert result.appkey == "APPKEY"
    assert result.body == (
        '{"orderSide":"BUY","orderType":"MARKET","origQty":0.001,"positionSide":"LONG","symbol":"BTCUSDT"}'
    )
    assert len(result.signature) == 64


def test_builder_signature_matches_exact_body():
    builder = XTFuturesTransportRequestBuilder(
        appkey="APPKEY",
        secret_key="SECRET",
    )

    result = builder.build(
        request=make_order_request(),
        timestamp="1234567890",
    )

    expected = builder.adapter.generate_body_signature(
        timestamp="1234567890",
        endpoint="/future/trade/v1/order/create",
        request_body=result.body,
    )

    assert result.signature == expected


def test_builder_rejects_missing_timestamp():
    builder = XTFuturesTransportRequestBuilder(
        appkey="APPKEY",
        secret_key="SECRET",
    )

    try:
        builder.build(
            request=make_order_request(),
            timestamp="",
        )
    except ValueError as exc:
        assert str(exc) == "timestamp is required"
    else:
        raise AssertionError("ValueError was not raised")
