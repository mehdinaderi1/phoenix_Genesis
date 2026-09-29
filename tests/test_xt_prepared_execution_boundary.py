from execution.paper_position_sizer import PaperPositionSizer
from execution.xt_futures_execution_orchestrator import (
    XTFuturesExecutionOrchestrator,
)
from intelligence.action_proposal import ActionProposal


def test_xt_prepared_execution_builds_approved_buy_order():
    proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        symbol="BTCUSDT",
        confidence=90,
        reason="approved test action",
    )

    sizer = PaperPositionSizer()
    quantity = sizer.calculate_quantity(
        balance=1000.0,
        position_size_percent=1.0,
        entry_price=50000.0,
    )

    orchestrator = XTFuturesExecutionOrchestrator()

    prepared = orchestrator.prepare(
        action_proposal=proposal,
        quantity=quantity,
        order_type="MARKET",
    )

    assert prepared is not None
    assert prepared["request"].symbol == "BTCUSDT"
    assert prepared["request"].order_side == "BUY"
    assert prepared["request"].position_side == "LONG"
    assert prepared["request"].quantity == quantity

    assert prepared["payload"] == {
        "symbol": "BTCUSDT",
        "orderSide": "BUY",
        "positionSide": "LONG",
        "orderType": "MARKET",
        "origQty": quantity,
    }

    assert prepared["idempotency_key"].value


def test_xt_prepared_execution_rejects_unapproved_action():
    proposal = ActionProposal(
        action="BUY",
        status="REJECTED",
        symbol="BTCUSDT",
        confidence=90,
    )

    orchestrator = XTFuturesExecutionOrchestrator()

    prepared = orchestrator.prepare(
        action_proposal=proposal,
        quantity=0.001,
    )

    assert prepared is None


def test_xt_prepared_execution_ignores_wait_action():
    proposal = ActionProposal(
        action="WAIT",
        status="APPROVED",
        symbol="BTCUSDT",
        confidence=90,
    )

    orchestrator = XTFuturesExecutionOrchestrator()

    prepared = orchestrator.prepare(
        action_proposal=proposal,
        quantity=0.001,
    )

    assert prepared is None
