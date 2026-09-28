from execution.xt_futures_transport_request import (
    XTFuturesTransportRequest
)


def test_transport_request_headers():
    request = XTFuturesTransportRequest(
        endpoint="/future/trade/v1/order/create",
        body='{"symbol":"BTCUSDT"}',
        timestamp="1234567890",
        appkey="APPKEY",
        signature="SIGNATURE",
    )

    assert request.headers() == {
        "Content-Type": "application/json",
        "validate-appkey": "APPKEY",
        "validate-timestamp": "1234567890",
        "validate-signature": "SIGNATURE",
    }


def test_transport_request_preserves_body():
    body = '{"symbol":"BTCUSDT","orderSide":"BUY"}'

    request = XTFuturesTransportRequest(
        endpoint="/future/trade/v1/order/create",
        body=body,
        timestamp="1234567890",
        appkey="APPKEY",
        signature="SIGNATURE",
    )

    assert request.body == body


def test_transport_request_is_immutable():
    request = XTFuturesTransportRequest(
        endpoint="/future/trade/v1/order/create",
        body="{}",
        timestamp="1234567890",
        appkey="APPKEY",
        signature="SIGNATURE",
    )

    try:
        request.body = '{"changed":true}'
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "Transport request must be immutable"
        )
