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
    def __init__(
        self,
        rejected_on_call=None,
        unknown_on_call=None,
    ):
        self.calls = []
        self.rejected_on_call = rejected_on_call
        self.unknown_on_call = unknown_on_call

    def get(self, endpoint, headers, timeout=10):
        self.calls.append(
            {
                "endpoint": endpoint,
                "headers": headers,
                "timeout": timeout,
            }
        )

        call_number = len(self.calls)
        order_id = str(100 + call_number)

        if (
            self.rejected_on_call is not None
            and call_number == self.rejected_on_call
        ):
            return HttpResponse(
                200,
                json.dumps(
                    {
                        "rc": 0,
                        "result": {
                            "orderId": order_id,
                            "state": "REJECTED",
                            "executedQty": "0",
                            "avgPrice": "68000",
                        },
                    }
                ),
            )

        if (
            self.unknown_on_call is not None
            and call_number == self.unknown_on_call
        ):
            return HttpResponse(
                200,
                json.dumps(
                    {
                        "rc": 0,
                        "result": {
                            "orderId": order_id,
                            "state": "PARTIALLY_FILLED",
                            "executedQty": "0.0001",
                            "avgPrice": "68000",
                        },
                    }
                ),
            )

        price = "50000" if call_number == 1 else "68000"

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


def build_shadow_runtime(detail_client):
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

    create_client = FakeCreateHttpClient()

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

    return session, shadow_runtime, orchestrator, create_client


def build_operational_runtime(detail_client):
    market_runtime = FakeMarketContextRuntime()
    intelligence = FakeIntelligenceFlow()
    paper_runtime = FakePaperTradingRuntime()
    archive = FakeArchive()

    session, shadow_runtime, orchestrator, create_client = (
        build_shadow_runtime(detail_client)
    )

    runtime = OperationalPaperRuntime(
        market_context_runtime=market_runtime,
        intelligence_flow=intelligence,
        paper_trading_runtime=paper_runtime,
        session_archive=archive,
        shadow_execution_runtime=shadow_runtime,
    )

    return (
        runtime,
        session,
        orchestrator,
        create_client,
        detail_client,
        paper_runtime,
    )


def test_operational_runtime_shadow_open_then_close_position_e2e():
    (
        runtime,
        session,
        orchestrator,
        create_client,
        detail_client,
        paper_runtime,
    ) = build_operational_runtime(
        FakeDetailHttpClient()
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

    assert len(create_client.calls) == 2
    assert len(detail_client.calls) == 2
    assert len(paper_runtime.cycles) == 2


def test_operational_runtime_shadow_rejected_close_preserves_position_and_finalizes_idempotency():
    (
        runtime,
        session,
        orchestrator,
        create_client,
        detail_client,
        paper_runtime,
    ) = build_operational_runtime(
        FakeDetailHttpClient(
            rejected_on_call=2,
        )
    )

    results = runtime.run(
        symbol="BTCUSDT",
        cycles=2,
    )

    assert len(results) == 2

    first = results[0]

    assert first["paper_result"]["action"] == "BUY"

    first_shadow = first["shadow_result"]

    assert first_shadow["status"] == "EXECUTED"

    first_execution = first_shadow["execution"]

    assert first_execution["reconciliation"].state.value == "CONFIRMED"

    first_result = first_execution["execution_result"]

    assert first_result is not None
    assert first_result.status == "EXECUTED"

    first_position = session.get_position()

    assert first_position is not None
    assert first_position.symbol == "BTCUSDT"
    assert first_position.side == "BUY"
    assert first_position.entry_price == 50000.0
    assert first_position.quantity == 0.0002

    second = results[1]

    assert second["paper_result"]["action"] == "SELL"

    second_shadow = second["shadow_result"]

    assert second_shadow["status"] == "EXECUTED"

    second_execution = second_shadow["execution"]

    assert second_execution["execution"]["state"] == "SENT"
    assert second_execution["execution"]["order_id"] == "102"
    assert second_execution["reconciliation"].state.value == "REJECTED"

    second_result = second_execution["execution_result"]

    assert second_result is None

    remaining_position = session.get_position()

    assert remaining_position is not None
    assert remaining_position.symbol == "BTCUSDT"
    assert remaining_position.side == "BUY"
    assert remaining_position.entry_price == 50000.0
    assert remaining_position.quantity == 0.0002

    assert session.get_trade_count() == 0
    assert session.get_balance() == 1000.0

    assert len(create_client.calls) == 2
    assert len(detail_client.calls) == 2

    second_idempotency_key = second_execution["idempotency_key"].value

    assert (
        orchestrator.idempotency_guard.get_state(
            second_idempotency_key
        ).value
        == "REJECTED"
    )


def test_operational_runtime_shadow_unknown_close_preserves_position_and_finalizes_idempotency():
    (
        runtime,
        session,
        orchestrator,
        create_client,
        detail_client,
        paper_runtime,
    ) = build_operational_runtime(
        FakeDetailHttpClient(
            unknown_on_call=2,
        )
    )

    results = runtime.run(
        symbol="BTCUSDT",
        cycles=2,
    )

    assert len(results) == 2

    first = results[0]

    assert first["paper_result"]["action"] == "BUY"

    first_shadow = first["shadow_result"]

    assert first_shadow["status"] == "EXECUTED"

    first_execution = first_shadow["execution"]

    assert first_execution["reconciliation"].state.value == "CONFIRMED"

    first_result = first_execution["execution_result"]

    assert first_result is not None
    assert first_result.status == "EXECUTED"

    first_position = session.get_position()

    assert first_position is not None
    assert first_position.symbol == "BTCUSDT"
    assert first_position.side == "BUY"
    assert first_position.entry_price == 50000.0
    assert first_position.quantity == 0.0002

    second = results[1]

    assert second["paper_result"]["action"] == "SELL"

    second_shadow = second["shadow_result"]

    assert second_shadow["status"] == "EXECUTED"

    second_execution = second_shadow["execution"]

    assert second_execution["execution"]["state"] == "SENT"
    assert second_execution["execution"]["order_id"] == "102"
    assert second_execution["reconciliation"].state.value == "UNKNOWN"

    second_result = second_execution["execution_result"]

    assert second_result is None

    remaining_position = session.get_position()

    assert remaining_position is not None
    assert remaining_position.symbol == "BTCUSDT"
    assert remaining_position.side == "BUY"
    assert remaining_position.entry_price == 50000.0
    assert remaining_position.quantity == 0.0002

    assert session.get_trade_count() == 0
    assert session.get_balance() == 1000.0

    assert len(create_client.calls) == 2
    assert len(detail_client.calls) == 2

    second_idempotency_key = second_execution["idempotency_key"].value

    assert (
        orchestrator.idempotency_guard.get_state(
            second_idempotency_key
        ).value
        == "UNKNOWN"
    )


def test_operational_runtime_shadow_rejected_close_recovers_on_next_cycle():
    detail_client = FakeDetailHttpClient(
        rejected_on_call=2,
    )

    (
        runtime,
        session,
        orchestrator,
        create_client,
        detail_client,
        paper_runtime,
    ) = build_operational_runtime(detail_client)

    # Cycle 1: OPEN position successfully.
    first_results = runtime.run(
        symbol="BTCUSDT",
        cycles=1,
    )

    first = first_results[0]
    first_shadow = first["shadow_result"]
    first_execution = first_shadow["execution"]

    assert first_shadow["status"] == "EXECUTED"
    assert first_execution["execution"]["state"] == "SENT"
    assert first_execution["execution"]["order_id"] == "101"
    assert first_execution["reconciliation"].state.value == "CONFIRMED"

    first_position = session.get_position()
    assert first_position is not None
    assert first_position.side == "BUY"

    first_key = first_shadow["idempotency_key"].value

    # Cycle 2: CLOSE is rejected.
    second_results = runtime.run(
        symbol="BTCUSDT",
        cycles=1,
    )

    second = second_results[0]
    second_shadow = second["shadow_result"]
    second_execution = second_shadow["execution"]

    assert second_shadow["status"] == "EXECUTED"
    assert second_execution["execution"]["state"] == "SENT"
    assert second_execution["execution"]["order_id"] == "102"
    assert second_execution["reconciliation"].state.value == "REJECTED"

    second_position = session.get_position()
    assert second_position is not None
    assert second_position.side == "BUY"

    rejected_key = second_shadow["idempotency_key"].value

    assert rejected_key != first_key
    assert (
        orchestrator.idempotency_guard.get_state(rejected_key).value
        == "REJECTED"
    )

    # Cycle 3: recovery must use a NEW attempt identity/key.
    third_results = runtime.run(
        symbol="BTCUSDT",
        cycles=1,
    )

    third = third_results[0]
    third_shadow = third["shadow_result"]
    third_execution = third_shadow["execution"]

    assert third_shadow["status"] == "EXECUTED"
    assert third_execution["execution"]["state"] == "SENT"
    assert third_execution["execution"]["order_id"] == "103"
    assert third_execution["reconciliation"].state.value == "CONFIRMED"

    recovery_key = third_shadow["idempotency_key"].value

    assert recovery_key != rejected_key
    assert recovery_key != first_key
    assert session.get_position() is None

    assert len(create_client.calls) == 3
    assert len(detail_client.calls) == 3


def test_operational_runtime_shadow_unknown_close_recovers_on_next_cycle():
    detail_client = FakeDetailHttpClient(
        unknown_on_call=2,
    )

    (
        runtime,
        session,
        orchestrator,
        create_client,
        detail_client,
        paper_runtime,
    ) = build_operational_runtime(detail_client)

    # Cycle 1: OPEN position successfully.
    first_results = runtime.run(
        symbol="BTCUSDT",
        cycles=1,
    )

    first = first_results[0]
    first_shadow = first["shadow_result"]
    first_execution = first_shadow["execution"]

    assert first_shadow["status"] == "EXECUTED"
    assert first_execution["execution"]["state"] == "SENT"
    assert first_execution["execution"]["order_id"] == "101"
    assert first_execution["reconciliation"].state.value == "CONFIRMED"

    first_position = session.get_position()
    assert first_position is not None
    assert first_position.side == "BUY"

    first_key = first_shadow["idempotency_key"].value

    # Cycle 2: CLOSE becomes UNKNOWN.
    second_results = runtime.run(
        symbol="BTCUSDT",
        cycles=1,
    )

    second = second_results[0]
    second_shadow = second["shadow_result"]
    second_execution = second_shadow["execution"]

    assert second_shadow["status"] == "EXECUTED"
    assert second_execution["execution"]["state"] == "SENT"
    assert second_execution["execution"]["order_id"] == "102"
    assert second_execution["reconciliation"].state.value == "UNKNOWN"
    assert second_execution["execution_result"] is None

    second_position = session.get_position()
    assert second_position is not None
    assert second_position.side == "BUY"
    assert second_position.quantity == 0.0002

    unknown_key = second_shadow["idempotency_key"].value

    assert unknown_key != first_key
    assert (
        orchestrator.idempotency_guard.get_state(unknown_key).value
        == "UNKNOWN"
    )

    # Cycle 3: recovery must use a NEW attempt identity/key.
    third_results = runtime.run(
        symbol="BTCUSDT",
        cycles=1,
    )

    third = third_results[0]
    third_shadow = third["shadow_result"]
    third_execution = third_shadow["execution"]

    assert third_shadow["status"] == "EXECUTED"
    assert third_execution["execution"]["state"] == "SENT"
    assert third_execution["execution"]["order_id"] == "103"
    assert third_execution["reconciliation"].state.value == "CONFIRMED"

    recovery_key = third_shadow["idempotency_key"].value

    assert recovery_key != unknown_key
    assert recovery_key != first_key

    third_result = third_execution["execution_result"]

    assert third_result is not None
    assert third_result.status == "EXECUTED"
    assert third_result.action == "SELL"
    assert third_result.symbol == "BTCUSDT"
    assert third_result.quantity == 0.0002
    assert third_result.price == 68000.0

    assert (
        orchestrator.idempotency_guard.get_state(recovery_key).value
        == "CONFIRMED"
    )

    assert session.get_position() is None
    assert session.get_trade_count() == 1
    assert session.get_balance() == 1003.6

    assert len(create_client.calls) == 3
    assert len(detail_client.calls) == 3
    assert len(paper_runtime.cycles) == 3
