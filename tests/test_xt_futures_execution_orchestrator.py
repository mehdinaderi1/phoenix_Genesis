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


def test_prepare_maps_action_to_xt_order():
    proposal = ActionProposal(
        action="BUY",
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


def test_prepare_maps_sell_to_short_when_flat():
    proposal = ActionProposal(
        action="SELL",
        symbol="BTCUSDT",
    )

    result = XTFuturesExecutionOrchestrator().prepare(
        action_proposal=proposal,
        quantity=0.001,
    )

    assert result["request"].order_side == "SELL"
    assert result["request"].position_side == "SHORT"


def test_execute_retries_and_preserves_idempotency():
    proposal = ActionProposal(
        action="BUY",
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
