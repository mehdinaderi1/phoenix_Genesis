from execution.http_client import HttpResponse
from execution.xt_futures_real_execution_gate import (
    XTFuturesRealExecutionGate,
)
from execution.xt_futures_order_request import XTFuturesOrderRequest
from intelligence.action_proposal import ActionProposal
from execution.xt_futures_real_execution_runtime import (
    XTFuturesRealExecutionRuntime,
)


class FakeBuilder:
    def __init__(self):
        self.calls = []

    def build(self, request, timestamp):
        self.calls.append((request, timestamp))
        return "TRANSPORT_REQUEST"


class FakeTransport:
    def __init__(self):
        self.calls = []

    def send(self, request):
        self.calls.append(request)
        return HttpResponse(
            200,
            '{"rc":0,"result":{"orderId":"123"}}',
        )


class FakeExecutionResult:
    def __init__(self, status):
        self.status = status


class FakeOrchestrator:
    def __init__(
        self,
        execution_state="SENT",
        execution_result=None,
    ):
        self.calls = []
        self.execute_calls = []
        self.execute_and_reconcile_calls = []
        self.execution_state = execution_state
        self.execution_result = execution_result

    def prepare(
        self,
        action_proposal,
        quantity,
        order_type,
    ):
        self.calls.append((
            action_proposal,
            quantity,
            order_type,
        ))

        return {
            "request": XTFuturesOrderRequest(
                symbol="BTCUSDT",
                order_side="BUY",
                position_side="LONG",
                order_type="MARKET",
                quantity=quantity,
            ),
            "payload": {
                "symbol": "BTCUSDT",
                "orderSide": "BUY",
                "positionSide": "LONG",
                "orderType": "MARKET",
                "origQty": quantity,
            },
            "idempotency_key": "test-key",
        }

    def execute(
        self,
        action_proposal,
        transport,
        quantity,
        order_type,
    ):
        self.execute_calls.append({
            "action_proposal": action_proposal,
            "quantity": quantity,
            "order_type": order_type,
        })

        response = transport()

        return {
            "execution": {
                "state": self.execution_state,
                "order_id": "123",
                "response": response,
            }
        }

    def execute_and_reconcile(
        self,
        action_proposal,
        transport,
        quantity,
        order_type,
    ):
        self.execute_and_reconcile_calls.append({
            "action_proposal": action_proposal,
            "quantity": quantity,
            "order_type": order_type,
        })

        response = transport()

        return {
            "execution": {
                "state": self.execution_state,
                "order_id": "123",
                "response": response,
            },
            "reconciliation": "CONFIRMED",
            "execution_result": self.execution_result,
        }


def approved_buy():
    return ActionProposal(
        action="BUY",
        status="APPROVED",
        symbol="BTCUSDT",
    )


def make_cycle():
    return {
        "action_proposal": approved_buy(),
        "price": 50000,
    }


def make_runtime(
    gate,
    builder,
    transport,
    orchestrator,
):
    return XTFuturesRealExecutionRuntime(
        balance=1000,
        position_size_percent=1.0,
        gate=gate,
        orchestrator=orchestrator,
        request_builder=builder,
        transport=transport,
        timestamp="123456",
    )


def test_real_execution_is_blocked_before_builder_and_transport():
    gate = XTFuturesRealExecutionGate(
        demo_mode=True,
        real_execution_enabled=False,
    )
    builder = FakeBuilder()
    transport = FakeTransport()
    orchestrator = FakeOrchestrator()

    runtime = make_runtime(
        gate=gate,
        builder=builder,
        transport=transport,
        orchestrator=orchestrator,
    )

    try:
        runtime.run([make_cycle()])
        assert False, "real execution should be blocked"
    except PermissionError as exc:
        assert "safety gate" in str(exc).lower()

    assert len(orchestrator.calls) == 0
    assert len(builder.calls) == 0
    assert len(transport.calls) == 0


def test_authorized_real_execution_reports_sent_state():
    gate = XTFuturesRealExecutionGate(
        demo_mode=False,
        real_execution_enabled=True,
    )
    builder = FakeBuilder()
    transport = FakeTransport()
    orchestrator = FakeOrchestrator(
        execution_state="SENT",
    )

    runtime = make_runtime(
        gate=gate,
        builder=builder,
        transport=transport,
        orchestrator=orchestrator,
    )

    results = runtime.run([make_cycle()])

    assert len(results) == 1
    assert results[0]["status"] == "SENT"
    assert results[0]["execution"] is not None

    assert len(orchestrator.calls) == 1
    assert len(orchestrator.execute_calls) == 0
    assert len(orchestrator.execute_and_reconcile_calls) == 1
    assert len(builder.calls) == 1
    assert len(transport.calls) == 1
    assert transport.calls[0] == "TRANSPORT_REQUEST"


def test_real_execution_reports_rejected_state():
    gate = XTFuturesRealExecutionGate(
        demo_mode=False,
        real_execution_enabled=True,
    )
    builder = FakeBuilder()
    transport = FakeTransport()
    orchestrator = FakeOrchestrator(
        execution_state="REJECTED",
    )

    runtime = make_runtime(
        gate=gate,
        builder=builder,
        transport=transport,
        orchestrator=orchestrator,
    )

    results = runtime.run([make_cycle()])

    assert len(results) == 1
    assert results[0]["status"] == "REJECTED"
    assert results[0]["execution"] is not None


def test_real_execution_reports_unknown_state():
    gate = XTFuturesRealExecutionGate(
        demo_mode=False,
        real_execution_enabled=True,
    )
    builder = FakeBuilder()
    transport = FakeTransport()
    orchestrator = FakeOrchestrator(
        execution_state="UNKNOWN",
    )

    runtime = make_runtime(
        gate=gate,
        builder=builder,
        transport=transport,
        orchestrator=orchestrator,
    )

    results = runtime.run([make_cycle()])

    assert len(results) == 1
    assert results[0]["status"] == "UNKNOWN"
    assert results[0]["execution"] is not None


def test_real_execution_enabled_is_not_enough_in_demo_mode():
    gate = XTFuturesRealExecutionGate(
        demo_mode=True,
        real_execution_enabled=True,
    )
    builder = FakeBuilder()
    transport = FakeTransport()
    orchestrator = FakeOrchestrator()

    runtime = make_runtime(
        gate=gate,
        builder=builder,
        transport=transport,
        orchestrator=orchestrator,
    )

    try:
        runtime.run([make_cycle()])
        assert False, "demo mode must block real execution"
    except PermissionError:
        pass

    assert len(orchestrator.calls) == 0
    assert len(builder.calls) == 0
    assert len(transport.calls) == 0


def test_real_execution_runtime_confirms_filled_order():
    gate = XTFuturesRealExecutionGate(
        demo_mode=False,
        real_execution_enabled=True,
    )
    builder = FakeBuilder()
    transport = FakeTransport()
    orchestrator = FakeOrchestrator(
        execution_state="SENT",
        execution_result=FakeExecutionResult(
            status="EXECUTED",
        ),
    )

    runtime = make_runtime(
        gate=gate,
        builder=builder,
        transport=transport,
        orchestrator=orchestrator,
    )

    results = runtime.run([make_cycle()])

    assert len(results) == 1
    assert results[0]["status"] == "EXECUTED"
    assert results[0]["execution"]["execution"]["state"] == "SENT"

    assert len(orchestrator.execute_calls) == 0
    assert len(orchestrator.execute_and_reconcile_calls) == 1


def test_real_execution_runtime_does_not_claim_execution_without_fill_evidence():
    gate = XTFuturesRealExecutionGate(
        demo_mode=False,
        real_execution_enabled=True,
    )
    builder = FakeBuilder()
    transport = FakeTransport()
    orchestrator = FakeOrchestrator(
        execution_state="SENT",
        execution_result=None,
    )

    runtime = make_runtime(
        gate=gate,
        builder=builder,
        transport=transport,
        orchestrator=orchestrator,
    )

    results = runtime.run([make_cycle()])

    assert len(results) == 1
    assert results[0]["status"] == "SENT"
    assert results[0]["execution"]["execution"]["state"] == "SENT"

    assert len(orchestrator.execute_calls) == 0
    assert len(orchestrator.execute_and_reconcile_calls) == 1