import pytest

from execution.xt_futures_attempt_state import (
    XTFuturesAttemptState,
)
from execution.xt_futures_confirmation_state_resolver import (
    XTFuturesConfirmationStateResolver,
)
from execution.xt_futures_order_confirmation import (
    XTFuturesOrderConfirmation,
    XTFuturesOrderConfirmationState,
)


def make_confirmation(
    state,
    order_id=None,
    error=None,
):
    return XTFuturesOrderConfirmation(
        state=state,
        order_id=order_id,
        error=error,
    )


def test_confirmed_maps_to_confirmed_attempt():
    confirmation = make_confirmation(
        XTFuturesOrderConfirmationState.CONFIRMED,
        order_id="123",
    )

    result = XTFuturesConfirmationStateResolver().resolve(
        idempotency_key="abc123",
        confirmation=confirmation,
    )

    assert result.state == XTFuturesAttemptState.CONFIRMED
    assert result.idempotency_key == "abc123"
    assert result.error is None


def test_rejected_maps_to_rejected_attempt():
    confirmation = make_confirmation(
        XTFuturesOrderConfirmationState.REJECTED,
        error="Order rejected",
    )

    result = XTFuturesConfirmationStateResolver().resolve(
        idempotency_key="abc123",
        confirmation=confirmation,
    )

    assert result.state == XTFuturesAttemptState.REJECTED
    assert result.error == "Order rejected"


def test_unknown_maps_to_unknown_attempt():
    confirmation = make_confirmation(
        XTFuturesOrderConfirmationState.UNKNOWN,
        error="Confirmation unavailable",
    )

    result = XTFuturesConfirmationStateResolver().resolve(
        idempotency_key="abc123",
        confirmation=confirmation,
    )

    assert result.state == XTFuturesAttemptState.UNKNOWN
    assert result.error == "Confirmation unavailable"


def test_unknown_without_error_gets_default_error():
    confirmation = make_confirmation(
        XTFuturesOrderConfirmationState.UNKNOWN,
    )

    result = XTFuturesConfirmationStateResolver().resolve(
        idempotency_key="abc123",
        confirmation=confirmation,
    )

    assert result.error == "Order state unknown"


def test_missing_key_is_rejected():
    confirmation = make_confirmation(
        XTFuturesOrderConfirmationState.UNKNOWN,
    )

    with pytest.raises(
        ValueError,
        match="idempotency_key is required",
    ):
        XTFuturesConfirmationStateResolver().resolve(
            idempotency_key="",
            confirmation=confirmation,
        )


def test_missing_confirmation_is_rejected():
    with pytest.raises(
        ValueError,
        match="confirmation is required",
    ):
        XTFuturesConfirmationStateResolver().resolve(
            idempotency_key="abc123",
            confirmation=None,
        )
