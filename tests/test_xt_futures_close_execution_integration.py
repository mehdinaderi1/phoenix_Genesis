from execution.http_client import HttpResponse
from execution.paper_trading_session import PaperTradingSession
from execution.xt_futures_attempt_state import XTFuturesAttemptState
from execution.xt_futures_execution_orchestrator import (
    XTFuturesExecutionOrchestrator,
)
from execution.xt_futures_order_confirmation import (
    XTFuturesOrderConfirmation,
    XTFuturesOrderConfirmationState,
)
from execution.xt_futures_position_bridge import XTFuturesPositionBridge
from execution.xt_futures_position_close_bridge import (
    XTFuturesPositionCloseBridge,
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


def make_proposal(action):
    return ActionProposal(
        action=action,
        symbol="BTCUSDT",
    )


def make_confirmed_confirmation(
    order_id="123",
    quantity=0.001,
    price=68000.0,
):
    return XTFuturesOrderConfirmation(
        state=XTFuturesOrderConfirmationState.CONFIRMED,
        order_id=order_id,
        executed_quantity=quantity,
        average_price=price,
    )


def make_transport():
    return FakeTransport([
        HttpResponse(
            200,
            '{"result":{"orderId":"123"}}',
        )
    ])


def test_confirmed_close_execution_closes_existing_long_position():
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0,
    )

    open_result = session.process_action(
        action_proposal=make_proposal("BUY"),
        price=67000.0,
        symbol="BTCUSDT",
    )

    position = open_result["position"]

    assert position is not None
    assert position.side == "BUY"

    expected_quantity = position.quantity

    position_bridge = XTFuturesPositionBridge(
        position_manager=session.position_manager,
    )

    close_bridge = XTFuturesPositionCloseBridge(
        session=session,
    )

    reconciliation_service = FakeReconciliationService(
        result=XTFuturesAttemptState.CONFIRMED,
        confirmation=make_confirmed_confirmation(
            quantity=expected_quantity,
            price=68000.0,
        ),
    )

    orchestrator = XTFuturesExecutionOrchestrator(
        reconciliation_service=reconciliation_service,
        position_bridge=position_bridge,
        position_close_bridge=close_bridge,
    )

    result = orchestrator.execute_and_reconcile(
        action_proposal=make_proposal("SELL"),
        transport=make_transport(),
        position=position,
        quantity=None,
        max_attempts=1,
    )

    assert result["request"].order_side == "SELL"
    assert result["request"].position_side == "LONG"
    assert result["request"].quantity == expected_quantity

    assert result["execution_result"] is not None
    assert result["execution_result"].status == "EXECUTED"
    assert result["execution_result"].price == 68000.0
    assert result["execution_result"].quantity == expected_quantity

    assert result["position"] is None
    assert session.get_position() is None
    assert session.get_trade_count() == 1

    expected_pnl = (
        68000.0 - position.entry_price
    ) * expected_quantity

    assert result["close"]["realized_pnl"] == expected_pnl

def test_close_execution_uses_existing_position_quantity():
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0,
    )

    open_result = session.process_action(
        action_proposal=make_proposal("BUY"),
        price=67000.0,
        symbol="BTCUSDT",
    )

    position = open_result["position"]

    assert position is not None

    expected_quantity = position.quantity

    position_bridge = XTFuturesPositionBridge(
        position_manager=session.position_manager,
    )

    close_bridge = XTFuturesPositionCloseBridge(
        session=session,
    )

    reconciliation_service = FakeReconciliationService(
        result=XTFuturesAttemptState.CONFIRMED,
        confirmation=make_confirmed_confirmation(
            quantity=expected_quantity,
            price=68000.0,
        ),
    )

    orchestrator = XTFuturesExecutionOrchestrator(
        reconciliation_service=reconciliation_service,
        position_bridge=position_bridge,
        position_close_bridge=close_bridge,
    )

    result = orchestrator.execute_and_reconcile(
        action_proposal=make_proposal("SELL"),
        transport=make_transport(),
        position=position,
        quantity=0.0001,
        max_attempts=1,
    )

    assert result["request"].quantity == expected_quantity
    assert result["request"].quantity != 0.0001
    assert result["execution_result"].quantity == expected_quantity
    assert result["position"] is None
    assert session.get_position() is None
    assert session.get_trade_count() == 1

def test_confirmed_close_execution_closes_existing_short_position():
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0,
    )

    open_result = session.process_action(
        action_proposal=make_proposal("SELL"),
        price=68000.0,
        symbol="BTCUSDT",
    )

    position = open_result["position"]

    assert position is not None
    assert position.side == "SELL"

    expected_quantity = position.quantity

    position_bridge = XTFuturesPositionBridge(
        position_manager=session.position_manager,
    )

    close_bridge = XTFuturesPositionCloseBridge(
        session=session,
    )

    reconciliation_service = FakeReconciliationService(
        result=XTFuturesAttemptState.CONFIRMED,
        confirmation=make_confirmed_confirmation(
            quantity=expected_quantity,
            price=67000.0,
        ),
    )

    orchestrator = XTFuturesExecutionOrchestrator(
        reconciliation_service=reconciliation_service,
        position_bridge=position_bridge,
        position_close_bridge=close_bridge,
    )

    result = orchestrator.execute_and_reconcile(
        action_proposal=make_proposal("BUY"),
        transport=make_transport(),
        position=position,
        quantity=None,
        max_attempts=1,
    )

    assert result["request"].order_side == "BUY"
    assert result["request"].position_side == "SHORT"
    assert result["request"].quantity == expected_quantity

    assert result["execution_result"] is not None
    assert result["execution_result"].status == "EXECUTED"
    assert result["execution_result"].price == 67000.0
    assert result["execution_result"].quantity == expected_quantity

    assert result["position"] is None
    assert session.get_position() is None
    assert session.get_trade_count() == 1

    expected_pnl = (
        position.entry_price - 67000.0
    ) * expected_quantity

    assert result["close"]["realized_pnl"] == expected_pnl
