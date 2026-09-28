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
    def __init__(
        self,
        result,
        confirmation=None,
    ):
        self.result = result
        self.confirmation = confirmation
        self.calls = []

    def reconcile(self, idempotency_key, order_id):
        self.calls.append(
            {
                "idempotency_key": idempotency_key,
                "order_id": order_id,
            }
        )
        return self.result

    def reconcile_with_confirmation(
        self,
        idempotency_key,
        order_id,
    ):
        self.calls.append(
            {
                "idempotency_key": idempotency_key,
                "order_id": order_id,
            }
        )

        return {
            "result": self.result,
            "confirmation": self.confirmation,
        }


def make_proposal():
    return ActionProposal(
        action="BUY",
        symbol="BTCUSDT",
    )


def make_confirmed_confirmation(
    order_id="123",
    quantity=0.001,
    price=67123.45,
):
    return XTFuturesOrderConfirmation(
        state=XTFuturesOrderConfirmationState.CONFIRMED,
        order_id=order_id,
        executed_quantity=quantity,
        average_price=price,
    )


def make_rejected_confirmation(
    order_id="456",
):
    return XTFuturesOrderConfirmation(
        state=XTFuturesOrderConfirmationState.REJECTED,
        order_id=order_id,
        error="Order state: REJECTED",
    )


def test_execute_and_reconcile_confirms_filled_order():
    service = FakeReconciliationService(
        XTFuturesAttemptState.CONFIRMED,
        confirmation=make_confirmed_confirmation(),
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

    execution_result = result["execution_result"]

    assert execution_result is not None
    assert execution_result.status == "EXECUTED"
    assert execution_result.action == "BUY"
    assert execution_result.symbol == "BTCUSDT"
    assert execution_result.quantity == 0.001
    assert execution_result.price == 67123.45

    assert service.calls == [
        {
            "idempotency_key": (
                result["idempotency_key"].value
            ),
            "order_id": 123,
        }
    ]


def test_execute_and_reconcile_preserves_rejected_result():
    service = FakeReconciliationService(
        XTFuturesAttemptState.REJECTED,
        confirmation=make_rejected_confirmation(),
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

    assert result["execution_result"] is None

    assert service.calls[0]["order_id"] == 456


def test_execute_and_reconcile_does_not_reconcile_timeout():
    service = FakeReconciliationService(
        XTFuturesAttemptState.CONFIRMED,
        confirmation=make_confirmed_confirmation(),
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
    assert result["execution_result"] is None
    assert service.calls == []


def test_execute_and_reconcile_does_not_reconcile_without_order_id():
    service = FakeReconciliationService(
        XTFuturesAttemptState.CONFIRMED,
        confirmation=make_confirmed_confirmation(),
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
    assert result["execution_result"] is None
    assert service.calls == []


def test_confirmed_without_fill_evidence_does_not_create_execution_result():
    confirmation = XTFuturesOrderConfirmation(
        state=XTFuturesOrderConfirmationState.CONFIRMED,
        order_id="789",
        executed_quantity=None,
        average_price=None,
    )

    service = FakeReconciliationService(
        XTFuturesAttemptState.CONFIRMED,
        confirmation=confirmation,
    )

    orchestrator = XTFuturesExecutionOrchestrator(
        reconciliation_service=service
    )

    transport = FakeTransport([
        HttpResponse(
            200,
            '{"result":{"orderId":"789"}}',
        ),
    ])

    result = orchestrator.execute_and_reconcile(
        action_proposal=make_proposal(),
        transport=transport,
        quantity=0.001,
        max_attempts=1,
    )

    assert result["reconciliation"] == (
        XTFuturesAttemptState.CONFIRMED
    )
    assert result["execution_result"] is None
