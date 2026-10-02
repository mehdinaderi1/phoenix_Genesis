import json

from execution.http_client import HttpResponse
from execution.xt_futures_execution_orchestrator import XTFuturesExecutionOrchestrator
from execution.xt_futures_order_detail_client import XTFuturesOrderDetailClient
from execution.xt_futures_order_detail_transport import XTFuturesOrderDetailTransport
from execution.xt_futures_order_detail_transport_request_builder import (
    XTFuturesOrderDetailTransportRequestBuilder,
)
from execution.xt_futures_order_reconciliation_service import (
    XTFuturesOrderReconciliationService,
)
from execution.xt_futures_position_bridge import XTFuturesPositionBridge
from execution.xt_futures_transport import XTFuturesTransport
from execution.xt_futures_transport_request_builder import (
    XTFuturesTransportRequestBuilder,
)
from intelligence.action_proposal import ActionProposal


class FakeCreateHttpClient:
    def __init__(self):
        self.calls = []

    def post(self, endpoint, headers, body, timeout=10):
        self.calls.append(
            {
                "endpoint": endpoint,
                "headers": headers,
                "body": body,
                "timeout": timeout,
            }
        )

        return HttpResponse(
            status_code=200,
            body=json.dumps(
                {
                    "rc": 0,
                    "result": {
                        "orderId": 1234567890,
                    },
                }
            ),
        )


class FakeDetailHttpClient:
    def __init__(self):
        self.calls = []

    def get(self, endpoint, headers, timeout=10):
        self.calls.append(
            {
                "endpoint": endpoint,
                "headers": headers,
                "timeout": timeout,
            }
        )

        return HttpResponse(
            status_code=200,
            body=json.dumps(
                {
                    "rc": 0,
                    "result": {
                        "orderId": 1234567890,
                        "state": "FILLED",
                        "executedQty": "0.001",
                        "avgPrice": "50000",
                    },
                }
            ),
        )


class FakePositionManager:
    def __init__(self):
        self.calls = []

    def open_position(self, execution_result, decision=None):
        self.calls.append(
            {
                "execution_result": execution_result,
                "decision": decision,
            }
        )

        return {
            "symbol": execution_result.symbol,
            "side": execution_result.action,
            "quantity": execution_result.quantity,
            "price": execution_result.price,
        }

    def get_position(self):
        return None


def test_orchestrator_uses_real_xt_create_transport_then_reconciles():
    proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        reason="integration test",
        confidence=95,
        symbol="BTCUSDT",
        strategy="TEST",
        risk_status="LOW",
    )

    position_manager = FakePositionManager()

    position_bridge = XTFuturesPositionBridge(
        position_manager=position_manager,
    )

    detail_http_client = FakeDetailHttpClient()

    detail_request_builder = XTFuturesOrderDetailTransportRequestBuilder(
        appkey="APPKEY",
        secret_key="SECRET",
        timestamp="1700000000000",
    )

    detail_transport = XTFuturesOrderDetailTransport(
        http_client=detail_http_client,
        timeout=15,
    )

    detail_client = XTFuturesOrderDetailClient(
        transport=detail_transport,
        request_builder=detail_request_builder,
    )

    reconciliation_service = XTFuturesOrderReconciliationService(
        detail_client=detail_client,
    )

    orchestrator = XTFuturesExecutionOrchestrator(
        reconciliation_service=reconciliation_service,
        position_bridge=position_bridge,
    )

    create_http_client = FakeCreateHttpClient()

    create_transport = XTFuturesTransport(
        http_client=create_http_client,
        timeout=20,
    )

    create_request_builder = XTFuturesTransportRequestBuilder(
        appkey="APPKEY",
        secret_key="SECRET",
    )

    prepared = orchestrator.prepare(
        action_proposal=proposal,
        quantity=0.001,
        order_type="MARKET",
    )

    assert prepared is not None

    transport_request = create_request_builder.build(
        request=prepared["request"],
        timestamp="1700000000000",
    )

    result = orchestrator.execute_and_reconcile(
        action_proposal=proposal,
        transport=lambda: create_transport.send(transport_request),
        quantity=0.001,
        order_type="MARKET",
    )

    assert result is not None

    assert len(create_http_client.calls) == 1

    create_call = create_http_client.calls[0]

    assert create_call["endpoint"] == (
        "/future/trade/v1/order/create"
    )

    assert create_call["timeout"] == 20

    assert create_call["headers"]["validate-appkey"] == "APPKEY"
    assert create_call["headers"]["validate-timestamp"] == (
        "1700000000000"
    )
    assert len(create_call["headers"]["validate-signature"]) == 64

    body = json.loads(create_call["body"])

    assert body == {
        "orderSide": "BUY",
        "orderType": "MARKET",
        "origQty": 0.001,
        "positionSide": "LONG",
        "symbol": "BTCUSDT",
    }

    assert result["execution"]["state"] == "SENT"
    assert result["execution"]["order_id"] == 1234567890

    assert result["reconciliation"].state.value == "CONFIRMED"

    execution_result = result["execution_result"]

    assert execution_result is not None
    assert execution_result.status == "EXECUTED"
    assert execution_result.action == "BUY"
    assert execution_result.symbol == "BTCUSDT"
    assert execution_result.quantity == 0.001
    assert execution_result.price == 50000.0

    assert result["position"] == {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "quantity": 0.001,
        "price": 50000.0,
    }

    assert len(position_manager.calls) == 1

    assert len(detail_http_client.calls) == 1
