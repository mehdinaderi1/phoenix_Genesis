from enum import Enum


class XTFuturesIdempotencyState(str, Enum):
    NEW = "NEW"
    SUBMITTED = "SUBMITTED"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


class XTFuturesExecutionIdempotencyGuard:
    """
    Prevents duplicate submission of the same logical XT Futures order
    within the current runtime session.

    This guard does not send network requests and does not reconcile
    exchange state. An existing key must be handled before a new
    submission is allowed.
    """

    def __init__(self):
        self._states = {}

    def can_submit(self, idempotency_key):
        if not idempotency_key:
            raise ValueError("idempotency key is required")

        return idempotency_key not in self._states

    def register(self, idempotency_key, state):
        if not idempotency_key:
            raise ValueError("idempotency key is required")

        if not isinstance(state, XTFuturesIdempotencyState):
            raise TypeError(
                "state must be XTFuturesIdempotencyState"
            )

        if idempotency_key in self._states:
            raise ValueError(
                "idempotency key is already registered"
            )

        self._states[idempotency_key] = state

    def update(self, idempotency_key, state):
        if not idempotency_key:
            raise ValueError("idempotency key is required")

        if not isinstance(state, XTFuturesIdempotencyState):
            raise TypeError(
                "state must be XTFuturesIdempotencyState"
            )

        if idempotency_key not in self._states:
            raise KeyError(
                "idempotency key is not registered"
            )

        self._states[idempotency_key] = state

    def get_state(self, idempotency_key):
        if not idempotency_key:
            raise ValueError("idempotency key is required")

        return self._states.get(idempotency_key)
