import json

from execution.http_client import HttpResponse
from execution.xt_futures_order_detail_client import XTFuturesOrderDetailClient
from execution.xt_futures_order_detail_transport import XTFuturesOrderDetailTransport
from execution.xt_futures_order_detail_transport_request_builder import (
    XTFuturesOrderDetailTransportRequestBuilder,
)
from execution.xt_futures_order_reconciliation_service import (
    XTFuturesOrderReconciliationService,
)
from execution.xt_futures_position_bridge import XTFuturesPositionBridge
from execution.xt_futures_shadow_execution_runtime import (
    XTFuturesShadowExecutionRuntime,
)
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
            200,
            json.dumps(
                {
                    "rc": 0,
                    "result": {
                        "orderId": "123",
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
            200,
            json.dumps(
                {
                    "rc": 0,
                    "result": {
                        "orderId": "123",
                        "state": "FILLED",
                        "executedQty": "0.0002",
                        "avgPrice": "50000",
                    },
                }
            ),
        )


class FakePositionManager:
    def __init__(self):
        self.calls = []

    def open_position(self, execution_result, decision=None):
        self.calls.append(execution_result)

        return {
            "symbol": execution_result.symbol,
            "side": execution_result.action,
            "quantity": execution_result.quantity,
            "price": execution_result.price,
        }

    def get_position(self):
        return None


def test_shadow_runtime_can_run_create_detail_reconciliation_lifecycle():
    create_client = FakeCreateHttpClient()
    detail_client = FakeDetailHttpClient()
    position_manager = FakePositionManager()

    create_transport = XTFuturesTransport(
        http_client=create_client,
        timeout=15,
    )

    create_builder = XTFuturesTransportRequestBuilder(
        appkey="APPKEY",
        secret_key="SECRET",
    )

    detail_transport = XTFuturesOrderDetailTransport(
        http_client=detail_client,
        timeout=15,
    )

    detail_builder = XTFuturesOrderDetailTransportRequestBuilder(
        appkey="APPKEY",
        secret_key="SECRET",
        timestamp="1234567890",
    )

    order_detail_client = XTFuturesOrderDetailClient(
        transport=detail_transport,
        request_builder=detail_builder,
    )

    reconciliation_service = XTFuturesOrderReconciliationService(
        detail_client=order_detail_client,
    )

    position_bridge = XTFuturesPositionBridge(
        position_manager=position_manager,
    )

    from execution.xt_futures_execution_orchestrator import (
        XTFuturesExecutionOrchestrator,
    )

    orchestrator = XTFuturesExecutionOrchestrator(
        reconciliation_service=reconciliation_service,
        position_bridge=position_bridge,
    )

    runtime = XTFuturesShadowExecutionRuntime(
        balance=1000,
        position_size_percent=1,
        orchestrator=orchestrator,
        transport=create_transport,
        request_builder=create_builder,
        timestamp="1234567890",
    )

    proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        symbol="BTCUSDT",
    )

    result = runtime.run(
        cycles=[
            {
                "action_proposal": proposal,
                "price": 50000,
            }
        ],
        symbol="BTCUSDT",
    )

    assert result[0]["status"] == "EXECUTED"

    execution = result[0]["execution"]

    assert execution["execution"]["state"] == "SENT"
    assert execution["execution"]["order_id"] == "123"

    assert execution["reconciliation"].state.value == "CONFIRMED"

    execution_result = execution["execution_result"]

    assert execution_result is not None
    assert execution_result.status == "EXECUTED"
    assert execution_result.action == "BUY"
    assert execution_result.symbol == "BTCUSDT"
    assert execution_result.quantity == 0.0002
    assert execution_result.price == 50000.0

    assert execution["position"] == {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "quantity": 0.0002,
        "price": 50000.0,
    }

    assert len(create_client.calls) == 1
    assert len(detail_client.calls) == 1
    assert len(position_manager.calls) == 1
