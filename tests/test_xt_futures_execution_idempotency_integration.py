import pytest

from execution.http_client import HttpResponse
from execution.xt_futures_response import XTFuturesResponse
from intelligence.action_proposal import ActionProposal
from execution.xt_futures_attempt_state import XTFuturesAttemptState
from execution.xt_futures_execution_idempotency_guard import (
    XTFuturesIdempotencyState,
)
from execution.xt_futures_execution_orchestrator import (
    XTFuturesExecutionOrchestrator,
)


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def __call__(self):
        response = self.responses[self.calls]
        self.calls += 1
        return response


def approved_buy():
    return ActionProposal(
        action="BUY",
        status="APPROVED",
        symbol="BTCUSDT",
    )


def test_same_logical_order_is_blocked_on_second_execution():
    transport = FakeTransport([
        HttpResponse(
            200,
            '{"rc":0,"result":{"orderId":"123"}}',
        ),
    ])

    orchestrator = XTFuturesExecutionOrchestrator()

    first = orchestrator.execute(
        action_proposal=approved_buy(),
        transport=transport,
        quantity=0.001,
    )

    assert first["execution"]["state"] == XTFuturesAttemptState.SENT
    assert transport.calls == 1

    with pytest.raises(
        PermissionError,
        match="Duplicate execution is blocked",
    ):
        orchestrator.execute(
            action_proposal=approved_buy(),
            transport=transport,
            quantity=0.001,
        )

    assert transport.calls == 1


def test_unknown_execution_blocks_replay():
    class TimeoutTransport:
        def __init__(self):
            self.calls = 0

        def __call__(self):
            self.calls += 1
            raise TimeoutError("timeout")

    transport = TimeoutTransport()
    orchestrator = XTFuturesExecutionOrchestrator()

    first = orchestrator.execute(
        action_proposal=approved_buy(),
        transport=transport,
        quantity=0.001,
        max_attempts=1,
    )

    assert first["execution"]["state"] == XTFuturesAttemptState.UNKNOWN
    assert transport.calls == 1

    key = first["idempotency_key"].value

    assert (
        orchestrator.idempotency_guard.get_state(key)
        == XTFuturesIdempotencyState.UNKNOWN
    )

    with pytest.raises(
        PermissionError,
        match="state=UNKNOWN",
    ):
        orchestrator.execute(
            action_proposal=approved_buy(),
            transport=transport,
            quantity=0.001,
            max_attempts=1,
        )

    assert transport.calls == 1


def test_different_logical_order_can_be_submitted():
    first_transport = FakeTransport([
        HttpResponse(
            200,
            '{"rc":0,"result":{"orderId":"123"}}',
        ),
    ])

    second_transport = FakeTransport([
        HttpResponse(
            200,
            '{"rc":0,"result":{"orderId":"456"}}',
        ),
    ])

    orchestrator = XTFuturesExecutionOrchestrator()

    first = orchestrator.execute(
        action_proposal=approved_buy(),
        transport=first_transport,
        quantity=0.001,
    )

    second = orchestrator.execute(
        action_proposal=approved_buy(),
        transport=second_transport,
        quantity=0.002,
    )

    assert first["execution"]["state"] == XTFuturesAttemptState.SENT
    assert second["execution"]["state"] == XTFuturesAttemptState.SENT
    assert first["idempotency_key"] != second["idempotency_key"]
    assert first_transport.calls == 1
    assert second_transport.calls == 1


def test_successful_reconciliation_marks_key_confirmed():
    class FakeDetailClient:
        def fetch(self, order_id):
            return XTFuturesResponse(
                status_code=200,
                ok=True,
                body={
                    "result": {
                        "orderId": "123",
                        "state": "FILLED",
                        "executedQty": "0.001",
                        "avgPrice": "50000",
                    }
                },
                raw_body=(
                    '{"rc":0,"result":{'
                    '"orderId":"123",'
                    '"state":"FILLED",'
                    '"executedQty":"0.001",'
                    '"avgPrice":"50000"'
                    '}}'
                ),
            )

    from execution.xt_futures_order_reconciliation_service import (
        XTFuturesOrderReconciliationService,
    )

    transport = FakeTransport([
        HttpResponse(
            200,
            '{"rc":0,"result":{"orderId":"123"}}',
        ),
    ])

    orchestrator = XTFuturesExecutionOrchestrator(
        reconciliation_service=(
            XTFuturesOrderReconciliationService(
                detail_client=FakeDetailClient()
            )
        )
    )

    result = orchestrator.execute_and_reconcile(
        action_proposal=approved_buy(),
        transport=transport,
        quantity=0.001,
    )

    key = result["idempotency_key"].value

    assert result["execution"]["state"] == XTFuturesAttemptState.SENT
    assert result["execution_result"].status == "EXECUTED"
    assert (
        orchestrator.idempotency_guard.get_state(key)
        == XTFuturesIdempotencyState.CONFIRMED
    )
