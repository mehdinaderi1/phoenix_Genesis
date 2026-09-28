import pytest

from execution.xt_futures_attempt_result import (
    XTFuturesAttemptResult,
)
from execution.xt_futures_attempt_state import (
    XTFuturesAttemptState,
)


def test_not_sent_state():
    result = XTFuturesAttemptResult(
        state=XTFuturesAttemptState.NOT_SENT,
        idempotency_key="abc123",
    )

    assert result.state == XTFuturesAttemptState.NOT_SENT
    assert result.error is None


def test_sent_state():
    result = XTFuturesAttemptResult(
        state=XTFuturesAttemptState.SENT,
        idempotency_key="abc123",
    )

    assert result.state == XTFuturesAttemptState.SENT


def test_confirmed_state():
    result = XTFuturesAttemptResult(
        state=XTFuturesAttemptState.CONFIRMED,
        idempotency_key="abc123",
    )

    assert result.state == XTFuturesAttemptState.CONFIRMED


def test_rejected_state_requires_error():
    result = XTFuturesAttemptResult(
        state=XTFuturesAttemptState.REJECTED,
        idempotency_key="abc123",
        error="Order rejected",
    )

    assert result.state == XTFuturesAttemptState.REJECTED
    assert result.error == "Order rejected"


def test_unknown_state():
    result = XTFuturesAttemptResult(
        state=XTFuturesAttemptState.UNKNOWN,
        idempotency_key="abc123",
    )

    assert result.state == XTFuturesAttemptState.UNKNOWN


def test_rejected_without_error_is_invalid():
    with pytest.raises(
        ValueError,
        match="REJECTED attempt requires error",
    ):
        XTFuturesAttemptResult(
            state=XTFuturesAttemptState.REJECTED,
            idempotency_key="abc123",
        )


def test_empty_idempotency_key_is_invalid():
    with pytest.raises(
        ValueError,
        match="idempotency_key is required",
    ):
        XTFuturesAttemptResult(
            state=XTFuturesAttemptState.NOT_SENT,
            idempotency_key="",
        )
