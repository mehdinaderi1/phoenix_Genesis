from execution.http_client import HttpResponse
from intelligence.action_proposal import ActionProposal
from execution.xt_futures_attempt_state import (
    XTFuturesAttemptState,
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


def test_prepare_maps_approved_action_to_xt_order():
    proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        symbol="BTCUSDT",
    )

    result = XTFuturesExecutionOrchestrator().prepare(
        action_proposal=proposal,
        quantity=0.001,
    )

    assert result is not None
    assert result["request"].symbol == "BTCUSDT"
    assert result["request"].order_side == "BUY"
    assert result["request"].position_side == "LONG"
    assert result["request"].order_type == "MARKET"
    assert result["request"].quantity == 0.001

    assert result["payload"]["symbol"] == "BTCUSDT"
    assert result["payload"]["orderSide"] == "BUY"
    assert result["payload"]["positionSide"] == "LONG"

    assert result["idempotency_key"].value


def test_prepare_maps_approved_sell_to_short_when_flat():
    proposal = ActionProposal(
        action="SELL",
        status="APPROVED",
        symbol="BTCUSDT",
    )

    result = XTFuturesExecutionOrchestrator().prepare(
        action_proposal=proposal,
        quantity=0.001,
    )

    assert result is not None
    assert result["request"].order_side == "SELL"
    assert result["request"].position_side == "SHORT"


def test_prepare_blocks_rejected_action_proposal():
    proposal = ActionProposal(
        action="BUY",
        status="REJECTED",
        symbol="BTCUSDT",
    )

    result = XTFuturesExecutionOrchestrator().prepare(
        action_proposal=proposal,
        quantity=0.001,
    )

    assert result is None


def test_prepare_blocks_pending_action_proposal():
    proposal = ActionProposal(
        action="BUY",
        status="PENDING",
        symbol="BTCUSDT",
    )

    result = XTFuturesExecutionOrchestrator().prepare(
        action_proposal=proposal,
        quantity=0.001,
    )

    assert result is None


def test_prepare_blocks_wait_action_even_when_approved():
    proposal = ActionProposal(
        action="WAIT",
        status="APPROVED",
        symbol="BTCUSDT",
    )

    result = XTFuturesExecutionOrchestrator().prepare(
        action_proposal=proposal,
        quantity=0.001,
    )

    assert result is None


def test_execute_retries_and_preserves_idempotency():
    proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        symbol="BTCUSDT",
    )

    transport = FakeTransport([
        HttpResponse(500, '{"error":"temporary"}'),
        HttpResponse(200, '{"result":{"orderId":"123"}}'),
    ])

    result = XTFuturesExecutionOrchestrator().execute(
        action_proposal=proposal,
        transport=transport,
        quantity=0.001,
        max_attempts=3,
    )

    assert result["execution"]["state"] == (
        XTFuturesAttemptState.SENT
    )
    assert transport.calls == 2
    assert result["idempotency_key"].value


def test_execute_returns_none_for_non_execution_action():
    proposal = ActionProposal(
        action="WAIT",
        status="APPROVED",
        symbol="BTCUSDT",
    )

    transport = FakeTransport([])

    result = XTFuturesExecutionOrchestrator().execute(
        action_proposal=proposal,
        transport=transport,
        quantity=0.001,
    )

    assert result is None
    assert transport.calls == 0


def test_execute_extracts_order_id_from_create_response():
    proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        symbol="BTCUSDT",
    )

    transport = FakeTransport([
        HttpResponse(
            200,
            '{"rc":0,"result":{"orderId":"123"}}',
        ),
    ])

    result = XTFuturesExecutionOrchestrator().execute(
        action_proposal=proposal,
        transport=transport,
        quantity=0.001,
    )

    assert result["execution"]["state"] == (
        XTFuturesAttemptState.SENT
    )
    assert result["execution"]["order_id"] == "123"


def test_execute_has_no_order_id_when_create_response_has_none():
    proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        symbol="BTCUSDT",
    )

    transport = FakeTransport([
        HttpResponse(
            200,
            '{"rc":0,"result":{}}',
        ),
    ])

    result = XTFuturesExecutionOrchestrator().execute(
        action_proposal=proposal,
        transport=transport,
        quantity=0.001,
    )

    assert result["execution"]["state"] == (
        XTFuturesAttemptState.SENT
    )
    assert result["execution"]["order_id"] is None


def test_execute_has_no_order_id_after_timeout():
    proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        symbol="BTCUSDT",
    )

    class TimeoutTransport:
        def __call__(self):
            raise TimeoutError("timeout")

    result = XTFuturesExecutionOrchestrator().execute(
        action_proposal=proposal,
        transport=TimeoutTransport(),
        quantity=0.001,
        max_attempts=1,
    )

    assert result["execution"]["state"] == (
        XTFuturesAttemptState.UNKNOWN
    )
    assert result["execution"]["order_id"] is None
