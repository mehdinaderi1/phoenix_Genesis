from execution.http_client import HttpResponse
from execution.xt_futures_shadow_execution_runtime import XTFuturesShadowExecutionRuntime
from execution.xt_futures_transport import XTFuturesTransport
from execution.xt_futures_transport_request_builder import XTFuturesTransportRequestBuilder
from intelligence.action_proposal import ActionProposal


class FakeHttpClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def post(self, endpoint, headers, body, timeout=10):
        self.calls.append({
            "endpoint": endpoint,
            "headers": headers,
            "body": body,
            "timeout": timeout,
        })
        return self.response


def test_shadow_runtime_prepares_approved_buy_without_real_transport():
    runtime = XTFuturesShadowExecutionRuntime(
        balance=1000,
        position_size_percent=1,
        transport=None,
        timestamp="1234567890",
    )

    proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        symbol="BTCUSDT",
    )

    result = runtime.run(
        cycles=[{"action_proposal": proposal, "price": 50000}],
        symbol="BTCUSDT",
    )

    assert result[0]["status"] == "PREPARED"
    assert result[0]["execution"] is None
    assert result[0]["request"].symbol == "BTCUSDT"
    assert result[0]["request"].order_side == "BUY"
    assert result[0]["request"].position_side == "LONG"
    assert result[0]["payload"]["origQty"] == 0.0002
    assert result[0]["idempotency_key"] is not None


def test_shadow_runtime_executes_through_injected_transport():
    client = FakeHttpClient(
        HttpResponse(
            200,
            '{"rc":0,"result":{"orderId":"123"}}',
        )
    )

    transport = XTFuturesTransport(
        http_client=client,
        timeout=15,
    )

    builder = XTFuturesTransportRequestBuilder(
        appkey="APPKEY",
        secret_key="SECRET",
    )

    runtime = XTFuturesShadowExecutionRuntime(
        balance=1000,
        position_size_percent=1,
        transport=transport,
        request_builder=builder,
        timestamp="1234567890",
    )

    proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        symbol="BTCUSDT",
    )

    result = runtime.run(
        cycles=[{"action_proposal": proposal, "price": 50000}],
        symbol="BTCUSDT",
    )

    assert result[0]["status"] == "EXECUTED"
    assert result[0]["execution"]["execution"]["state"] == "SENT"
    assert result[0]["execution"]["execution"]["order_id"] == "123"
    assert len(client.calls) == 1
    assert client.calls[0]["endpoint"] == (
        "/future/trade/v1/order/create"
    )
    assert client.calls[0]["headers"]["validate-appkey"] == "APPKEY"
    assert client.calls[0]["headers"]["validate-timestamp"] == "1234567890"
