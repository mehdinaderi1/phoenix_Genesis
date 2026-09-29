from execution.http_client import HttpResponse
from execution.xt_futures_execution_orchestrator import (
    XTFuturesExecutionOrchestrator,
)
from execution.xt_futures_transport import XTFuturesTransport
from execution.xt_futures_transport_request_builder import (
    XTFuturesTransportRequestBuilder,
)
from intelligence.action_proposal import ActionProposal


class FakeHttpClient:
    def __init__(self):
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
        return HttpResponse(
            200,
            '{"rc":0,"result":{"orderId":"123"}}'
        )


def test_orchestrator_executes_through_builder_and_transport():
    client = FakeHttpClient()
    transport = XTFuturesTransport(
        http_client=client
    )
    builder = XTFuturesTransportRequestBuilder(
        appkey="APPKEY",
        secret_key="SECRET",
    )

    proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        symbol="BTCUSDT",
        confidence=90,
    )

    orchestrator = XTFuturesExecutionOrchestrator()

    prepared_holder = {}

    def transport_callable():
        request = prepared_holder["request"]
        transport_request = builder.build(
            request=request,
            timestamp="1234567890",
        )
        prepared_holder["transport_request"] = transport_request
        return transport.send(transport_request)

    prepared = orchestrator.prepare(
        action_proposal=proposal,
        quantity=0.001,
        order_type="MARKET",
    )

    assert prepared is not None
    prepared_holder["request"] = prepared["request"]

    result = orchestrator.execute(
        action_proposal=proposal,
        transport=transport_callable,
        quantity=0.001,
        order_type="MARKET",
        max_attempts=1,
    )

    assert result is not None
    assert result["execution"]["state"] == "SENT"
    assert result["execution"]["order_id"] == "123"

    assert len(client.calls) == 1
    assert client.calls[0]["endpoint"] == (
        "/future/trade/v1/order/create"
    )
    assert client.calls[0]["body"] == (
        prepared_holder["transport_request"].body
    )
    assert client.calls[0]["headers"]["validate-appkey"] == (
        "APPKEY"
    )
    assert client.calls[0]["headers"]["validate-timestamp"] == (
        "1234567890"
    )
    assert client.calls[0]["headers"]["validate-signature"] == (
        prepared_holder["transport_request"].signature
    )
