import json

from core.market_data.operational_paper_runtime import OperationalPaperRuntime
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


class FakeObservation:
    symbol = "BTCUSDT"
    price = 50000.0
    source_status = "LIVE"


class FakeMarketContext:
    symbol = "BTCUSDT"
    trend = "BULLISH"
    signal = "BUY"
    confidence = 90
    consensus_breakdown = {}


class FakeMarketContextRuntime:
    def run_cycle(self, symbol="BTCUSDT", timeframes=None):
        return {
            "observation": FakeObservation(),
            "context": FakeMarketContext(),
            "candle_boundaries": {},
        }


class FakeIntelligenceFlow:
    def create_report(self, consensus):
        proposal = ActionProposal(
            action="PREPARE_LONG",
            status="APPROVED",
            symbol="BTCUSDT",
            confidence=90,
            reason="approved end-to-end integration test",
        )

        class Report:
            action_proposal = proposal
            decision = None
            signal = "BUY"
            trend = "BULLISH"
            regime = "TREND"
            confidence = 90
            risk = "LOW"

        return Report()


class FakePaperTradingRuntime:
    def __init__(self):
        self.cycles = []

        class Session:
            session_id = "test-session"

        self.session = Session()

    def run(self, cycles, symbol="BTCUSDT"):
        self.cycles.extend(cycles)

        return [
            {
                "action": "BUY",
                "position": None,
                "realized_pnl": 0.0,
                "learning_result": None,
            }
            for _ in cycles
        ]

    def build_summary(self, paper_results):
        return {
            "current_position": None,
            "realized_pnl": 0.0,
        }


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


class FakeArchive:
    def save(self, session_id, record):
        self.session_id = session_id
        self.record = record


def test_operational_runtime_connects_shadow_reconciliation_and_position_lifecycle():
    market_runtime = FakeMarketContextRuntime()
    intelligence = FakeIntelligenceFlow()
    paper_runtime = FakePaperTradingRuntime()
    archive = FakeArchive()

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

    shadow_runtime = XTFuturesShadowExecutionRuntime(
        balance=1000,
        position_size_percent=1,
        orchestrator=orchestrator,
        transport=create_transport,
        request_builder=create_builder,
        timestamp="1234567890",
    )

    runtime = OperationalPaperRuntime(
        market_context_runtime=market_runtime,
        intelligence_flow=intelligence,
        paper_trading_runtime=paper_runtime,
        session_archive=archive,
        shadow_execution_runtime=shadow_runtime,
    )

    results = runtime.run(
        symbol="BTCUSDT",
        cycles=1,
    )

    assert len(results) == 1

    result = results[0]

    assert result["paper_result"]["action"] == "BUY"

    shadow_result = result["shadow_result"]

    assert shadow_result["status"] == "EXECUTED"

    execution = shadow_result["execution"]

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
    assert len(paper_runtime.cycles) == 1
