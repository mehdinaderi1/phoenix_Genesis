import pytest

from execution.xt_futures_error_classifier import XTFuturesErrorType
from execution.xt_futures_retry_policy import (
    XTFuturesRetryDecision,
    XTFuturesRetryPolicy,
)


@pytest.fixture
def policy():
    return XTFuturesRetryPolicy()


def test_success_is_not_retryable(policy):
    assert policy.decide(
        XTFuturesErrorType.NONE,
        200
    ) == XTFuturesRetryDecision.NO_RETRY


def test_parse_error_is_not_retryable(policy):
    assert policy.decide(
        XTFuturesErrorType.PARSE,
        200
    ) == XTFuturesRetryDecision.NO_RETRY


def test_business_error_is_not_retryable(policy):
    assert policy.decide(
        XTFuturesErrorType.BUSINESS,
        200
    ) == XTFuturesRetryDecision.NO_RETRY


def test_http_408_is_retryable(policy):
    assert policy.decide(
        XTFuturesErrorType.HTTP,
        408
    ) == XTFuturesRetryDecision.RETRY


def test_http_429_is_retryable(policy):
    assert policy.decide(
        XTFuturesErrorType.HTTP,
        429
    ) == XTFuturesRetryDecision.RETRY


@pytest.mark.parametrize(
    "status_code",
    [500, 502, 503, 504, 599]
)
def test_server_errors_are_retryable(
    policy,
    status_code
):
    assert policy.decide(
        XTFuturesErrorType.HTTP,
        status_code
    ) == XTFuturesRetryDecision.RETRY


@pytest.mark.parametrize(
    "status_code",
    [400, 401, 403, 404, 409, 422]
)
def test_client_errors_are_not_retryable(
    policy,
    status_code
):
    assert policy.decide(
        XTFuturesErrorType.HTTP,
        status_code
    ) == XTFuturesRetryDecision.NO_RETRY


def test_unknown_http_status_is_not_retryable(policy):
    assert policy.decide(
        XTFuturesErrorType.HTTP,
        None
    ) == XTFuturesRetryDecision.NO_RETRY


def test_invalid_error_type_is_rejected(policy):
    with pytest.raises(
        TypeError,
        match="error_type must be XTFuturesErrorType"
    ):
        policy.decide("HTTP", 500)
