from execution.http_client import HttpResponse
from execution.paper_position_manager import PaperPositionManager
from execution.xt_futures_attempt_state import XTFuturesAttemptState
from execution.xt_futures_execution_orchestrator import (
    XTFuturesExecutionOrchestrator,
)
from execution.xt_futures_order_confirmation import (
    XTFuturesOrderConfirmation,
    XTFuturesOrderConfirmationState,
)
from execution.xt_futures_position_bridge import (
    XTFuturesPositionBridge,
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
    def __init__(self, result, confirmation):
        self.result = result
        self.confirmation = confirmation

    def reconcile_with_confirmation(self, idempotency_key, order_id):
        return {
            "result": self.result,
            "confirmation": self.confirmation,
        }


def make_proposal(action="BUY"):
    return ActionProposal(
        action=action,
        status="APPROVED",
        symbol="BTCUSDT",
    )


def make_confirmed_confirmation():
    return XTFuturesOrderConfirmation(
        state=XTFuturesOrderConfirmationState.CONFIRMED,
        order_id="123",
        executed_quantity=0.001,
        average_price=67123.45,
    )


def make_rejected_confirmation():
    return XTFuturesOrderConfirmation(
        state=XTFuturesOrderConfirmationState.REJECTED,
        order_id="123",
        error="Order state: REJECTED",
    )


def make_unknown_confirmation():
    return XTFuturesOrderConfirmation(
        state=XTFuturesOrderConfirmationState.UNKNOWN,
        order_id="123",
        error="Order state: NEW",
    )


def make_orchestrator(confirmation, state):
    position_manager = PaperPositionManager()
    position_bridge = XTFuturesPositionBridge(
        position_manager=position_manager
    )

    reconciliation_service = FakeReconciliationService(
        result=state,
        confirmation=confirmation,
    )

    orchestrator = XTFuturesExecutionOrchestrator(
        reconciliation_service=reconciliation_service,
        position_bridge=position_bridge,
    )

    return orchestrator, position_manager


def test_confirmed_filled_execution_creates_position():
    orchestrator, position_manager = make_orchestrator(
        confirmation=make_confirmed_confirmation(),
        state=XTFuturesAttemptState.CONFIRMED,
    )

    transport = FakeTransport([
        HttpResponse(
            200,
            '{"result":{"orderId":"123"}}',
        )
    ])

    result = orchestrator.execute_and_reconcile(
        action_proposal=make_proposal(),
        transport=transport,
        quantity=0.001,
        max_attempts=1,
    )

    assert result["execution_result"] is not None
    assert result["execution_result"].status == "EXECUTED"

    position = result["position"]

    assert position is not None
    assert position.symbol == "BTCUSDT"
    assert position.side == "BUY"
    assert position.entry_price == 67123.45
    assert position.quantity == 0.001

    assert position_manager.get_position() is position


def test_rejected_execution_does_not_create_position():
    orchestrator, position_manager = make_orchestrator(
        confirmation=make_rejected_confirmation(),
        state=XTFuturesAttemptState.REJECTED,
    )

    transport = FakeTransport([
        HttpResponse(
            200,
            '{"result":{"orderId":"123"}}',
        )
    ])

    result = orchestrator.execute_and_reconcile(
        action_proposal=make_proposal(),
        transport=transport,
        quantity=0.001,
        max_attempts=1,
    )

    assert result["execution_result"] is None
    assert result["position"] is None
    assert position_manager.get_position() is None


def test_unknown_execution_does_not_create_position():
    orchestrator, position_manager = make_orchestrator(
        confirmation=make_unknown_confirmation(),
        state=XTFuturesAttemptState.UNKNOWN,
    )

    transport = FakeTransport([
        HttpResponse(
            200,
            '{"result":{"orderId":"123"}}',
        )
    ])

    result = orchestrator.execute_and_reconcile(
        action_proposal=make_proposal(),
        transport=transport,
        quantity=0.001,
        max_attempts=1,
    )

    assert result["execution_result"] is None
    assert result["position"] is None
    assert position_manager.get_position() is None


def test_sent_without_confirmation_does_not_create_position():
    orchestrator, position_manager = make_orchestrator(
        confirmation=None,
        state=XTFuturesAttemptState.CONFIRMED,
    )

    transport = FakeTransport([
        HttpResponse(
            200,
            '{"result":{"orderId":"123"}}',
        )
    ])

    # Replace reconciliation result with no usable confirmation.
    orchestrator.reconciliation_service.confirmation = None

    try:
        result = orchestrator.execute_and_reconcile(
            action_proposal=make_proposal(),
            transport=transport,
            quantity=0.001,
            max_attempts=1,
        )
    except TypeError:
        result = None

    assert result is None or result["position"] is None
    assert position_manager.get_position() is None
