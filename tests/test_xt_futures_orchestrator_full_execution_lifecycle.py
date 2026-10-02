import json

from execution.http_client import HttpResponse
from execution.paper_position_manager import PaperPositionManager
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
from intelligence.action_proposal import ActionProposal


class FakeCreateTransport:
    def __init__(self):
        self.calls = 0

    def __call__(self):
        self.calls += 1
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
        self.position = None

    def open_position(self, execution_result, decision=None):
        self.calls.append(
            {
                "execution_result": execution_result,
                "decision": decision,
            }
        )
        self.position = {
            "symbol": execution_result.symbol,
            "side": execution_result.action,
            "quantity": execution_result.quantity,
            "price": execution_result.price,
        }
        return self.position

    def get_position(self):
        return self.position


def test_orchestrator_create_confirm_and_position_lifecycle():
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

    create_transport = FakeCreateTransport()

    result = orchestrator.execute_and_reconcile(
        action_proposal=proposal,
        transport=create_transport,
        quantity=0.001,
        order_type="MARKET",
    )

    assert result is not None

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

    assert create_transport.calls == 1

    assert len(detail_http_client.calls) == 1

    detail_call = detail_http_client.calls[0]

    assert detail_call["endpoint"] == (
        "https://fapi.xt.com"
        "/future/trade/v1/order/detail?"
        "orderId=1234567890"
    )

    assert detail_call["timeout"] == 15
    assert detail_call["headers"]["validate-appkey"] == "APPKEY"
    assert detail_call["headers"]["validate-timestamp"] == "1700000000000"
    assert len(detail_call["headers"]["validate-signature"]) == 64

    assert len(position_manager.calls) == 1
