import pytest

from execution.http_client import HttpResponse
from execution.xt_futures_attempt_state import (
    XTFuturesAttemptState,
)
from execution.xt_futures_retry_executor import (
    XTFuturesRetryExecutor,
)


class FakeTransport:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    def __call__(self):
        outcome = self.outcomes[self.calls]
        self.calls += 1

        if isinstance(outcome, Exception):
            raise outcome

        return outcome


def test_500_then_200_retries_and_stops_on_success():
    transport = FakeTransport([
        HttpResponse(500, '{"error":"temporary"}'),
        HttpResponse(200, '{"result":{"orderId":"123"}}'),
    ])

    result = XTFuturesRetryExecutor().execute(
        transport=transport,
        idempotency_key="abc123",
        max_attempts=3,
    )

    assert result["state"] == XTFuturesAttemptState.SENT
    assert transport.calls == 2
    assert len(result["attempts"]) == 2


def test_repeated_500_stops_at_max_attempts():
    transport = FakeTransport([
        HttpResponse(500, '{"error":"temporary"}'),
        HttpResponse(500, '{"error":"temporary"}'),
        HttpResponse(500, '{"error":"temporary"}'),
    ])

    result = XTFuturesRetryExecutor().execute(
        transport=transport,
        idempotency_key="abc123",
        max_attempts=3,
    )

    assert result["state"] == XTFuturesAttemptState.REJECTED
    assert transport.calls == 3


def test_400_is_not_retried():
    transport = FakeTransport([
        HttpResponse(400, '{"error":"bad request"}'),
    ])

    result = XTFuturesRetryExecutor().execute(
        transport=transport,
        idempotency_key="abc123",
        max_attempts=3,
    )

    assert result["state"] == XTFuturesAttemptState.REJECTED
    assert transport.calls == 1


def test_parse_error_is_not_retried():
    transport = FakeTransport([
        HttpResponse(200, "not-json"),
        HttpResponse(200, '{"result":{"orderId":"123"}}'),
    ])

    result = XTFuturesRetryExecutor().execute(
        transport=transport,
        idempotency_key="abc123",
        max_attempts=3,
    )

    assert result["state"] == XTFuturesAttemptState.UNKNOWN
    assert transport.calls == 1


def test_timeout_can_retry_to_success():
    transport = FakeTransport([
        TimeoutError("timeout"),
        HttpResponse(200, '{"result":{"orderId":"123"}}'),
    ])

    result = XTFuturesRetryExecutor().execute(
        transport=transport,
        idempotency_key="abc123",
        max_attempts=2,
    )

    assert result["state"] == XTFuturesAttemptState.SENT
    assert transport.calls == 2
    assert result["attempts"][0]["state"] == (
        XTFuturesAttemptState.UNKNOWN
    )


def test_network_error_stops_at_max_attempts():
    transport = FakeTransport([
        OSError("connection reset"),
        OSError("connection reset"),
    ])

    result = XTFuturesRetryExecutor().execute(
        transport=transport,
        idempotency_key="abc123",
        max_attempts=2,
    )

    assert result["state"] == XTFuturesAttemptState.UNKNOWN
    assert transport.calls == 2


def test_invalid_transport_is_rejected():
    with pytest.raises(
        TypeError,
        match="transport must be callable",
    ):
        XTFuturesRetryExecutor().execute(
            transport=None,
            idempotency_key="abc123",
        )


def test_invalid_key_is_rejected():
    with pytest.raises(
        ValueError,
        match="idempotency_key is required",
    ):
        XTFuturesRetryExecutor().execute(
            transport=lambda: HttpResponse(
                200,
                '{"result":{}}',
            ),
            idempotency_key="",
        )


def test_invalid_max_attempts_is_rejected():
    with pytest.raises(
        ValueError,
        match="max_attempts must be greater than zero",
    ):
        XTFuturesRetryExecutor().execute(
            transport=lambda: HttpResponse(
                200,
                '{"result":{}}',
            ),
            idempotency_key="abc123",
            max_attempts=0,
        )

def test_500_then_200_preserves_final_response():
    transport = FakeTransport([
        HttpResponse(500, '{"error":"temporary"}'),
        HttpResponse(
            200,
            '{"rc":0,"result":{"orderId":"123"}}',
        ),
    ])

    result = XTFuturesRetryExecutor().execute(
        transport=transport,
        idempotency_key="abc123",
        max_attempts=3,
    )

    assert result["state"] == XTFuturesAttemptState.SENT
    assert transport.calls == 2

    response = result["response"]

    assert response.status_code == 200
    assert response.ok is True
    assert response.body["result"]["orderId"] == "123"


def test_final_response_is_preserved_for_success():
    transport = FakeTransport([
        HttpResponse(
            200,
            '{"rc":0,"result":{"orderId":"456"}}',
        ),
    ])

    result = XTFuturesRetryExecutor().execute(
        transport=transport,
        idempotency_key="abc123",
        max_attempts=3,
    )

    assert result["state"] == XTFuturesAttemptState.SENT
    assert result["response"].body["result"]["orderId"] == "456"


def test_unknown_timeout_has_no_response():
    transport = FakeTransport([
        TimeoutError("timeout"),
    ])

    result = XTFuturesRetryExecutor().execute(
        transport=transport,
        idempotency_key="abc123",
        max_attempts=1,
    )

    assert result["state"] == XTFuturesAttemptState.UNKNOWN
    assert result["response"] is None
