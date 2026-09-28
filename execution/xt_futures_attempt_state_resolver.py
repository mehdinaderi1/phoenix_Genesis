from execution.xt_futures_attempt_result import XTFuturesAttemptResult
from execution.xt_futures_attempt_state import XTFuturesAttemptState
from execution.xt_futures_error_classifier import XTFuturesErrorType


class XTFuturesAttemptStateResolver:
    """
    Resolves the known state of an XT Futures execution attempt.

    This resolver is deliberately conservative:
    a successful HTTP transport response is SENT, not CONFIRMED,
    until XT business-response semantics are verified.
    """

    def resolve(
        self,
        idempotency_key,
        error_type,
        status_code=None,
        error=None,
    ):
        if not idempotency_key:
            raise ValueError(
                "idempotency_key is required"
            )

        if not isinstance(
            error_type,
            XTFuturesErrorType
        ):
            raise TypeError(
                "error_type must be XTFuturesErrorType"
            )

        if error_type == XTFuturesErrorType.NONE:
            return XTFuturesAttemptResult(
                state=XTFuturesAttemptState.SENT,
                idempotency_key=idempotency_key,
            )

        if error_type == XTFuturesErrorType.HTTP:
            return XTFuturesAttemptResult(
                state=XTFuturesAttemptState.REJECTED,
                idempotency_key=idempotency_key,
                error=error or (
                    f"HTTP {status_code}"
                ),
            )

        if error_type in (
            XTFuturesErrorType.PARSE,
        ):
            return XTFuturesAttemptResult(
                state=XTFuturesAttemptState.UNKNOWN,
                idempotency_key=idempotency_key,
                error=error or "Response could not be parsed",
            )

        if error_type == XTFuturesErrorType.BUSINESS:
            return XTFuturesAttemptResult(
                state=XTFuturesAttemptState.REJECTED,
                idempotency_key=idempotency_key,
                error=error or "Business rejection",
            )

        return XTFuturesAttemptResult(
            state=XTFuturesAttemptState.UNKNOWN,
            idempotency_key=idempotency_key,
            error=error or "Unknown execution state",
        )
