from execution.http_client import HttpResponse
from execution.xt_futures_order_request import XTFuturesOrderRequest
from execution.xt_futures_retry_executor import XTFuturesRetryExecutor
from execution.xt_futures_transport import XTFuturesTransport
from execution.xt_futures_transport_request_builder import (
    XTFuturesTransportRequestBuilder,
)


class FakeHttpClient:
    def __init__(self, responses):
        self.responses = list(responses)
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
        return self.responses[len(self.calls) - 1]


def make_order_request():
    return XTFuturesOrderRequest(
        symbol="BTCUSDT",
        order_side="BUY",
        position_side="LONG",
        order_type="MARKET",
        quantity=0.001,
    )


def test_builder_transport_and_retry_work_together():
    client = FakeHttpClient([
        HttpResponse(500, '{"error":"temporary"}'),
        HttpResponse(200, '{"rc":0,"result":{"orderId":"123"}}'),
    ])

    transport = XTFuturesTransport(
        http_client=client,
        timeout=15,
    )

    builder = XTFuturesTransportRequestBuilder(
        appkey="APPKEY",
        secret_key="SECRET",
    )

    transport_request = builder.build(
        request=make_order_request(),
        timestamp="1234567890",
    )

    retry_result = XTFuturesRetryExecutor().execute(
        transport=lambda: transport.send(transport_request),
        idempotency_key="shadow-test-key",
        max_attempts=3,
    )

    assert retry_result["state"] == "SENT"
    assert len(retry_result["attempts"]) == 2
    assert len(client.calls) == 2

    assert client.calls[0]["endpoint"] == (
        "/future/trade/v1/order/create"
    )
    assert client.calls[0]["body"] == transport_request.body

    assert client.calls[0]["headers"] == {
        "Content-Type": "application/json",
        "validate-appkey": "APPKEY",
        "validate-timestamp": "1234567890",
        "validate-signature": transport_request.signature,
    }

    assert client.calls[1]["body"] == client.calls[0]["body"]
    assert client.calls[1]["headers"] == client.calls[0]["headers"]


def test_transport_error_reaches_existing_retry_executor():
    class FailingHttpClient:
        def post(
            self,
            endpoint,
            headers,
            body,
            timeout=10
        ):
            raise TimeoutError("shadow timeout")

    transport = XTFuturesTransport(
        http_client=FailingHttpClient()
    )

    builder = XTFuturesTransportRequestBuilder(
        appkey="APPKEY",
        secret_key="SECRET",
    )

    request = builder.build(
        request=make_order_request(),
        timestamp="1234567890",
    )

    result = XTFuturesRetryExecutor().execute(
        transport=lambda: transport.send(request),
        idempotency_key="shadow-timeout-key",
        max_attempts=1,
    )

    assert result["response"] is None
    assert result["attempts"][0]["error"] == "shadow timeout"
