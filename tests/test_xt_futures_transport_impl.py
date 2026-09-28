import pytest

from execution.http_client import HttpResponse
from execution.xt_futures_transport import (
    XTFuturesTransport
)
from execution.xt_futures_transport_request import (
    XTFuturesTransportRequest
)


class FakeHttpClient:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def post(
        self,
        endpoint,
        headers,
        body,
        timeout=10
    ):
        self.calls.append({
            "endpoint": endpoint,
            "headers": headers,
            "body": body,
            "timeout": timeout,
        })

        if self.error is not None:
            raise self.error

        return self.response


def make_request():
    return XTFuturesTransportRequest(
        endpoint="/future/trade/v1/order/create",
        body='{"symbol":"BTCUSDT"}',
        timestamp="1234567890",
        appkey="APPKEY",
        signature="SIGNATURE",
    )


def test_transport_sends_request():
    client = FakeHttpClient(
        response=HttpResponse(
            status_code=200,
            body='{"rc":0}'
        )
    )

    transport = XTFuturesTransport(
        http_client=client,
        timeout=15
    )

    response = transport.send(
        make_request()
    )

    assert response.status_code == 200
    assert response.body == '{"rc":0}'

    assert len(client.calls) == 1

    call = client.calls[0]

    assert call["endpoint"] == (
        "/future/trade/v1/order/create"
    )

    assert call["body"] == '{"symbol":"BTCUSDT"}'
    assert call["timeout"] == 15

    assert call["headers"] == {
        "Content-Type": "application/json",
        "validate-appkey": "APPKEY",
        "validate-timestamp": "1234567890",
        "validate-signature": "SIGNATURE",
    }


def test_transport_propagates_http_client_error():
    error = TimeoutError("request timed out")

    client = FakeHttpClient(
        error=error
    )

    transport = XTFuturesTransport(
        http_client=client
    )

    with pytest.raises(
        TimeoutError,
        match="request timed out"
    ):
        transport.send(
            make_request()
        )


def test_transport_rejects_invalid_request():
    client = FakeHttpClient()

    transport = XTFuturesTransport(
        http_client=client
    )

    with pytest.raises(
        TypeError,
        match="request must be XTFuturesTransportRequest"
    ):
        transport.send({
            "endpoint": "/test"
        })


def test_transport_does_not_modify_request():
    client = FakeHttpClient(
        response=HttpResponse(
            status_code=200,
            body="{}"
        )
    )

    transport = XTFuturesTransport(
        http_client=client
    )

    request = make_request()

    transport.send(request)

    assert request.endpoint == (
        "/future/trade/v1/order/create"
    )

    assert request.body == (
        '{"symbol":"BTCUSDT"}'
    )

    assert request.timestamp == "1234567890"
    assert request.appkey == "APPKEY"
    assert request.signature == "SIGNATURE"
