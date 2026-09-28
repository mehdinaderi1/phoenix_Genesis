import pytest

from execution.xt_futures_attempt_state import (
    XTFuturesAttemptState,
)
from execution.xt_futures_attempt_state_resolver import (
    XTFuturesAttemptStateResolver,
)
from execution.xt_futures_error_classifier import (
    XTFuturesErrorType,
)


@pytest.fixture
def resolver():
    return XTFuturesAttemptStateResolver()


def test_successful_transport_is_sent_not_confirmed(
    resolver,
):
    result = resolver.resolve(
        idempotency_key="abc123",
        error_type=XTFuturesErrorType.NONE,
        status_code=200,
    )

    assert result.state == XTFuturesAttemptState.SENT


def test_http_400_is_rejected(resolver):
    result = resolver.resolve(
        idempotency_key="abc123",
        error_type=XTFuturesErrorType.HTTP,
        status_code=400,
    )

    assert result.state == XTFuturesAttemptState.REJECTED
    assert result.error == "HTTP 400"


def test_http_500_is_rejected(resolver):
    result = resolver.resolve(
        idempotency_key="abc123",
        error_type=XTFuturesErrorType.HTTP,
        status_code=500,
    )

    assert result.state == XTFuturesAttemptState.REJECTED
    assert result.error == "HTTP 500"


def test_parse_error_is_unknown(resolver):
    result = resolver.resolve(
        idempotency_key="abc123",
        error_type=XTFuturesErrorType.PARSE,
    )

    assert result.state == XTFuturesAttemptState.UNKNOWN


def test_business_error_is_rejected(resolver):
    result = resolver.resolve(
        idempotency_key="abc123",
        error_type=XTFuturesErrorType.BUSINESS,
        error="Order rejected by exchange",
    )

    assert result.state == XTFuturesAttemptState.REJECTED
    assert result.error == "Order rejected by exchange"


def test_invalid_error_type_is_rejected(resolver):
    with pytest.raises(
        TypeError,
        match="error_type must be XTFuturesErrorType",
    ):
        resolver.resolve(
            idempotency_key="abc123",
            error_type="INVALID",
        )


def test_missing_key_is_rejected(resolver):
    with pytest.raises(
        ValueError,
        match="idempotency_key is required",
    ):
        resolver.resolve(
            idempotency_key="",
            error_type=XTFuturesErrorType.NONE,
        )


def test_none_error_type_is_rejected(resolver):
    with pytest.raises(
        TypeError,
        match="error_type must be XTFuturesErrorType",
    ):
        resolver.resolve(
            idempotency_key="abc123",
            error_type=None,
        )
