import pytest

from execution.xt_futures_execution_idempotency_guard import (
    XTFuturesExecutionIdempotencyGuard,
    XTFuturesIdempotencyState,
)


@pytest.fixture
def guard():
    return XTFuturesExecutionIdempotencyGuard()


def test_new_key_can_be_submitted(guard):
    assert guard.can_submit("key-1") is True


def test_registered_key_cannot_be_submitted_again(guard):
    guard.register(
        "key-1",
        XTFuturesIdempotencyState.SUBMITTED,
    )

    assert guard.can_submit("key-1") is False


@pytest.mark.parametrize(
    "state",
    [
        XTFuturesIdempotencyState.SUBMITTED,
        XTFuturesIdempotencyState.CONFIRMED,
        XTFuturesIdempotencyState.REJECTED,
        XTFuturesIdempotencyState.UNKNOWN,
    ],
)
def test_existing_state_blocks_replay(guard, state):
    guard.register("key-1", state)

    assert guard.can_submit("key-1") is False
    assert guard.get_state("key-1") == state


def test_different_keys_are_independent(guard):
    guard.register(
        "key-1",
        XTFuturesIdempotencyState.SUBMITTED,
    )

    assert guard.can_submit("key-1") is False
    assert guard.can_submit("key-2") is True


def test_state_can_be_updated(guard):
    guard.register(
        "key-1",
        XTFuturesIdempotencyState.SUBMITTED,
    )

    guard.update(
        "key-1",
        XTFuturesIdempotencyState.CONFIRMED,
    )

    assert (
        guard.get_state("key-1")
        == XTFuturesIdempotencyState.CONFIRMED
    )


def test_duplicate_registration_is_rejected(guard):
    guard.register(
        "key-1",
        XTFuturesIdempotencyState.SUBMITTED,
    )

    with pytest.raises(
        ValueError,
        match="already registered",
    ):
        guard.register(
            "key-1",
            XTFuturesIdempotencyState.SUBMITTED,
        )


def test_update_unknown_key_is_rejected(guard):
    with pytest.raises(
        KeyError,
        match="not registered",
    ):
        guard.update(
            "key-1",
            XTFuturesIdempotencyState.UNKNOWN,
        )


def test_empty_key_is_rejected(guard):
    with pytest.raises(
        ValueError,
        match="idempotency key is required",
    ):
        guard.can_submit("")


def test_invalid_state_is_rejected(guard):
    with pytest.raises(
        TypeError,
        match="state must be XTFuturesIdempotencyState",
    ):
        guard.register("key-1", "SUBMITTED")
