import pytest
from execution.http_client import HttpResponse
from execution.xt_futures_order_detail_client import XTFuturesOrderDetailClient
from execution.xt_futures_order_detail_transport import XTFuturesOrderDetailTransport
from execution.xt_futures_order_detail_transport_request_builder import XTFuturesOrderDetailTransportRequestBuilder


class FakeHttpClient:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def get(self, endpoint, headers, timeout=10):
        self.calls.append({
            "endpoint": endpoint,
            "headers": headers,
            "timeout": timeout,
        })
        if self.error is not None:
            raise self.error
        return self.response


def test_order_detail_transport_sends_signed_get():
    client = FakeHttpClient(
        response=HttpResponse(
            status_code=200,
            body='{"rc":0,"result":{"orderId":1234567890,"state":"FILLED"}}'
        )
    )

    builder = XTFuturesOrderDetailTransportRequestBuilder(
        appkey="APPKEY",
        secret_key="SECRET",
        timestamp="1700000000000",
    )

    transport = XTFuturesOrderDetailTransport(
        http_client=client,
        timeout=15,
    )

    response = transport.fetch(
        order_id=1234567890,
        request_builder=builder,
    )

    assert response.status_code == 200
    assert len(client.calls) == 1

    call = client.calls[0]
    assert call["endpoint"] == (
        "https://fapi.xt.com"
        "/future/trade/v1/order/detail?"
        "orderId=1234567890"
    )
    assert call["timeout"] == 15
    assert call["headers"]["validate-appkey"] == "APPKEY"
    assert call["headers"]["validate-timestamp"] == "1700000000000"
    assert len(call["headers"]["validate-signature"]) == 64


def test_order_detail_client_fetches_order_detail():
    client = FakeHttpClient(
        response=HttpResponse(
            status_code=200,
            body='{"rc":0,"result":{"orderId":1234567890,"state":"FILLED","executedQty":"0.001","avgPrice":"50000"}}'
        )
    )

    builder = XTFuturesOrderDetailTransportRequestBuilder(
        appkey="APPKEY",
        secret_key="SECRET",
        timestamp="1700000000000",
    )

    transport = XTFuturesOrderDetailTransport(
        http_client=client,
    )

    detail_client = XTFuturesOrderDetailClient(
        transport=transport,
        request_builder=builder,
    )

    response = detail_client.fetch(1234567890)

    assert response.status_code == 200
    assert len(client.calls) == 1
    assert client.calls[0]["endpoint"].endswith(
        "orderId=1234567890"
    )


def test_order_detail_transport_propagates_http_error():
    client = FakeHttpClient(
        error=TimeoutError("request timed out")
    )

    transport = XTFuturesOrderDetailTransport(
        http_client=client,
    )

    with pytest.raises(
        TimeoutError,
        match="request timed out"
    ):
        transport.fetch(
            order_id=1234567890,
            request_builder=XTFuturesOrderDetailTransportRequestBuilder(
                appkey="APPKEY",
                secret_key="SECRET",
                timestamp="1700000000000",
            ),
        )
