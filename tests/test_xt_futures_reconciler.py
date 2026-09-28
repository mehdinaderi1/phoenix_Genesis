from execution.xt_futures_attempt_state import XTFuturesAttemptState
from execution.xt_futures_order_confirmation import (
    XTFuturesOrderConfirmation,
    XTFuturesOrderConfirmationState,
)
from execution.xt_futures_reconciler import XTFuturesReconciler


def test_confirmed_order_reconciliation():
    confirmation = XTFuturesOrderConfirmation(
        state=XTFuturesOrderConfirmationState.CONFIRMED,
        order_id="123",
    )

    result = XTFuturesReconciler().reconcile(
        idempotency_key="idem-123",
        confirmation=confirmation,
    )

    assert result.state == XTFuturesAttemptState.CONFIRMED
    assert result.idempotency_key == "idem-123"


def test_rejected_order_reconciliation():
    confirmation = XTFuturesOrderConfirmation(
        state=XTFuturesOrderConfirmationState.REJECTED,
        order_id="123",
        error="Order state: CANCELED",
    )

    result = XTFuturesReconciler().reconcile(
        idempotency_key="idem-123",
        confirmation=confirmation,
    )

    assert result.state == XTFuturesAttemptState.REJECTED
    assert result.idempotency_key == "idem-123"
    assert result.error == "Order state: CANCELED"


def test_unknown_order_reconciliation_remains_unknown():
    confirmation = XTFuturesOrderConfirmation(
        state=XTFuturesOrderConfirmationState.UNKNOWN,
        order_id="123",
        error="Order state: NEW",
    )

    result = XTFuturesReconciler().reconcile(
        idempotency_key="idem-123",
        confirmation=confirmation,
    )

    assert result.state == XTFuturesAttemptState.UNKNOWN
    assert result.idempotency_key == "idem-123"
    assert result.error == "Order state: NEW"


def test_reconciliation_requires_idempotency_key():
    confirmation = XTFuturesOrderConfirmation(
        state=XTFuturesOrderConfirmationState.UNKNOWN,
        order_id="123",
    )

    try:
        XTFuturesReconciler().reconcile(
            idempotency_key="",
            confirmation=confirmation,
        )
        assert False
    except ValueError:
        pass


def test_reconciliation_requires_confirmation():
    try:
        XTFuturesReconciler().reconcile(
            idempotency_key="idem-123",
            confirmation=None,
        )
        assert False
    except ValueError:
        pass
