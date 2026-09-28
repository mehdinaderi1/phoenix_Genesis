from execution.http_client import HttpResponse
from execution.xt_futures_attempt_state import (
    XTFuturesAttemptState,
)
from execution.xt_futures_execution_orchestrator import (
    XTFuturesExecutionOrchestrator,
)
from execution.xt_futures_order_confirmation import (
    XTFuturesOrderConfirmation,
    XTFuturesOrderConfirmationState,
)
from intelligence.action_proposal import ActionProposal


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def __call__(self):
        response = self.responses[self.calls]
        self.calls += 1
        return response


class FakeReconciliationService:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def reconcile(self, idempotency_key, order_id):
        self.calls.append(
            {
                "idempotency_key": idempotency_key,
                "order_id": order_id,
            }
        )
        return self.result


def make_proposal():
    return ActionProposal(
        action="BUY",
        symbol="BTCUSDT",
    )


def test_execute_and_reconcile_confirms_filled_order():
    reconciliation_result = XTFuturesAttemptState.CONFIRMED

    service = FakeReconciliationService(
        reconciliation_result
    )

    orchestrator = XTFuturesExecutionOrchestrator(
        reconciliation_service=service
    )

    transport = FakeTransport([
        HttpResponse(
            200,
            '{"result":{"orderId":"123"}}',
        ),
    ])

    result = orchestrator.execute_and_reconcile(
        action_proposal=make_proposal(),
        transport=transport,
        quantity=0.001,
        max_attempts=1,
    )

    assert result["execution"]["state"] == (
        XTFuturesAttemptState.SENT
    )
    assert result["execution"]["order_id"] == "123"

    assert result["reconciliation"] == (
        XTFuturesAttemptState.CONFIRMED
    )

    assert service.calls == [
        {
            "idempotency_key": (
                result["idempotency_key"].value
            ),
            "order_id": 123,
        }
    ]


def test_execute_and_reconcile_preserves_rejected_result():
    reconciliation_result = XTFuturesAttemptState.REJECTED

    service = FakeReconciliationService(
        reconciliation_result
    )

    orchestrator = XTFuturesExecutionOrchestrator(
        reconciliation_service=service
    )

    transport = FakeTransport([
        HttpResponse(
            200,
            '{"result":{"orderId":"456"}}',
        ),
    ])

    result = orchestrator.execute_and_reconcile(
        action_proposal=make_proposal(),
        transport=transport,
        quantity=0.001,
        max_attempts=1,
    )

    assert result["execution"]["state"] == (
        XTFuturesAttemptState.SENT
    )
    assert result["reconciliation"] == (
        XTFuturesAttemptState.REJECTED
    )
    assert service.calls[0]["order_id"] == 456


def test_execute_and_reconcile_does_not_reconcile_timeout():
    service = FakeReconciliationService(
        XTFuturesAttemptState.CONFIRMED
    )

    class TimeoutTransport:
        def __call__(self):
            raise TimeoutError("timeout")

    orchestrator = XTFuturesExecutionOrchestrator(
        reconciliation_service=service
    )

    result = orchestrator.execute_and_reconcile(
        action_proposal=make_proposal(),
        transport=TimeoutTransport(),
        quantity=0.001,
        max_attempts=1,
    )

    assert result["execution"]["state"] == (
        XTFuturesAttemptState.UNKNOWN
    )
    assert result["execution"]["order_id"] is None
    assert result["reconciliation"] is None
    assert service.calls == []


def test_execute_and_reconcile_does_not_reconcile_without_order_id():
    service = FakeReconciliationService(
        XTFuturesAttemptState.CONFIRMED
    )

    orchestrator = XTFuturesExecutionOrchestrator(
        reconciliation_service=service
    )

    transport = FakeTransport([
        HttpResponse(
            200,
            '{"result":{}}',
        ),
    ])

    result = orchestrator.execute_and_reconcile(
        action_proposal=make_proposal(),
        transport=transport,
        quantity=0.001,
        max_attempts=1,
    )

    assert result["execution"]["state"] == (
        XTFuturesAttemptState.SENT
    )
    assert result["execution"]["order_id"] is None
    assert result["reconciliation"] is None
    assert service.calls == []
