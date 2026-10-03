import json

from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from execution.http_client import HttpResponse
from execution.paper_trading_session import PaperTradingSession
from execution.xt_futures_order_detail_client import XTFuturesOrderDetailClient
from execution.xt_futures_order_detail_transport import XTFuturesOrderDetailTransport
from execution.xt_futures_order_detail_transport_request_builder import (
    XTFuturesOrderDetailTransportRequestBuilder,
)
from execution.xt_futures_order_reconciliation_service import (
    XTFuturesOrderReconciliationService,
)
from execution.xt_futures_position_bridge import XTFuturesPositionBridge
from execution.xt_futures_position_close_bridge import XTFuturesPositionCloseBridge
from execution.xt_futures_shadow_execution_runtime import (
    XTFuturesShadowExecutionRuntime,
)
from execution.xt_futures_transport import XTFuturesTransport
from execution.xt_futures_transport_request_builder import (
    XTFuturesTransportRequestBuilder,
)
from execution.xt_futures_execution_orchestrator import (
    XTFuturesExecutionOrchestrator,
)
from intelligence.action_proposal import ActionProposal


class FakeObservation:
    def __init__(self, price):
        self.symbol = "BTCUSDT"
        self.price = price
        self.source_status = "LIVE"


class FakeMarketContext:
    def __init__(self, price, signal):
        self.symbol = "BTCUSDT"
        self.trend = "BULLISH" if signal == "BUY" else "BEARISH"
        self.signal = signal
        self.confidence = 90
        self.consensus_breakdown = {}


class FakeMarketContextRuntime:
    def __init__(self):
        self.calls = 0

    def run_cycle(self, symbol="BTCUSDT", timeframes=None):
        self.calls += 1

        if self.calls == 1:
            price = 50000.0
            signal = "BUY"
        else:
            price = 68000.0
            signal = "SELL"

        return {
            "observation": FakeObservation(price),
            "context": FakeMarketContext(price, signal),
            "candle_boundaries": {},
        }


class FakeIntelligenceFlow:
    def __init__(self):
        self.calls = 0

    def create_report(self, consensus):
        self.calls += 1

        if self.calls == 1:
            action = "PREPARE_LONG"
            signal = "BUY"
            trend = "BULLISH"
        else:
            action = "PREPARE_SHORT"
            signal = "SELL"
            trend = "BEARISH"

        proposal = ActionProposal(
            action=action,
            status="APPROVED",
            symbol="BTCUSDT",
            confidence=90,
            reason=f"approved cycle {self.calls}",
        )

        report = type(
            "Report",
            (),
            {
                "action_proposal": proposal,
                "decision": None,
                "signal": signal,
                "trend": trend,
                "regime": "TREND",
                "confidence": 90,
                "risk": "LOW",
            },
        )()

        return report


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
                "action": cycle["action_proposal"].action.replace(
                    "PREPARE_LONG", "BUY"
                ).replace(
                    "PREPARE_SHORT", "SELL"
                ),
                "position": None,
                "realized_pnl": 0.0,
                "learning_result": None,
            }
            for cycle in cycles
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

        order_id = str(100 + len(self.calls))

        return HttpResponse(
            200,
            json.dumps(
                {
                    "rc": 0,
                    "result": {
                        "orderId": order_id,
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

        order_id = str(100 + len(self.calls))

        price = "50000" if len(self.calls) == 1 else "68000"

        return HttpResponse(
            200,
            json.dumps(
                {
                    "rc": 0,
                    "result": {
                        "orderId": order_id,
                        "state": "FILLED",
                        "executedQty": "0.0002",
                        "avgPrice": price,
                    },
                }
            ),
        )


class FakeArchive:
    def save(self, session_id, record):
        self.session_id = session_id
        self.record = record


def test_operational_runtime_shadow_open_then_close_position_e2e():
    market_runtime = FakeMarketContextRuntime()
    intelligence = FakeIntelligenceFlow()
    paper_runtime = FakePaperTradingRuntime()
    archive = FakeArchive()

    create_client = FakeCreateHttpClient()
    detail_client = FakeDetailHttpClient()

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0,
    )

    position_bridge = XTFuturesPositionBridge(
        position_manager=session.position_manager,
    )

    position_close_bridge = XTFuturesPositionCloseBridge(
        session=session,
    )

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

    orchestrator = XTFuturesExecutionOrchestrator(
        reconciliation_service=reconciliation_service,
        position_bridge=position_bridge,
        position_close_bridge=position_close_bridge,
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
        cycles=2,
    )

    assert len(results) == 2

    # =========================================================
    # Cycle 1: Operational BUY -> Shadow FILLED -> Position OPEN
    # =========================================================

    first = results[0]

    assert first["paper_result"]["action"] == "BUY"

    first_shadow = first["shadow_result"]

    assert first_shadow["status"] == "EXECUTED"

    first_execution = first_shadow["execution"]

    assert first_execution["execution"]["state"] == "SENT"
    assert first_execution["execution"]["order_id"] == "101"
    assert first_execution["reconciliation"].state.value == "CONFIRMED"

    first_result = first_execution["execution_result"]

    assert first_result is not None
    assert first_result.status == "EXECUTED"
    assert first_result.action == "BUY"
    assert first_result.symbol == "BTCUSDT"
    assert first_result.quantity == 0.0002
    assert first_result.price == 50000.0

    first_position = first_execution["position"]

    assert first_position is not None
    assert first_position.symbol == "BTCUSDT"
    assert first_position.side == "BUY"
    assert first_position.entry_price == 50000.0
    assert first_position.quantity == 0.0002

    # =========================================================
    # Cycle 2: Operational SELL -> Shadow FILLED -> Position CLOSE
    # =========================================================

    second = results[1]

    assert second["paper_result"]["action"] == "SELL"

    second_shadow = second["shadow_result"]

    assert second_shadow["status"] == "EXECUTED"

    second_execution = second_shadow["execution"]

    assert second_execution["execution"]["state"] == "SENT"
    assert second_execution["execution"]["order_id"] == "102"
    assert second_execution["reconciliation"].state.value == "CONFIRMED"

    second_result = second_execution["execution_result"]

    assert second_result is not None
    assert second_result.status == "EXECUTED"
    assert second_result.action == "SELL"
    assert second_result.symbol == "BTCUSDT"
    assert second_result.quantity == 0.0002
    assert second_result.price == 68000.0

    assert session.get_position() is None
    assert session.get_trade_count() == 1

    # 0.0002 BTC * (68000 - 50000) = +3.6
    assert session.get_balance() == 1003.6

    # Two complete create + detail reconciliation cycles.
    assert len(create_client.calls) == 2
    assert len(detail_client.calls) == 2
    assert len(paper_runtime.cycles) == 2
