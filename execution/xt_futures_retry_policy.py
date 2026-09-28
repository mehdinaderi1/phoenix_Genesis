from enum import Enum

from execution.xt_futures_error_classifier import XTFuturesErrorType


class XTFuturesRetryDecision(str, Enum):
    RETRY = "RETRY"
    NO_RETRY = "NO_RETRY"


class XTFuturesRetryPolicy:
    """
    Decides whether an XT Futures failure is retryable.

    This policy does not perform retries.
    """

    def decide(
        self,
        error_type: XTFuturesErrorType,
        status_code: int | None = None
    ) -> XTFuturesRetryDecision:

        if not isinstance(
            error_type,
            XTFuturesErrorType
        ):
            raise TypeError(
                "error_type must be XTFuturesErrorType"
            )

        if error_type == XTFuturesErrorType.NONE:
            return XTFuturesRetryDecision.NO_RETRY

        if error_type == XTFuturesErrorType.NETWORK:
            return XTFuturesRetryDecision.RETRY

        if error_type in (
            XTFuturesErrorType.PARSE,
            XTFuturesErrorType.BUSINESS,
        ):
            return XTFuturesRetryDecision.NO_RETRY

        if error_type == XTFuturesErrorType.HTTP:
            if status_code in (408, 429):
                return XTFuturesRetryDecision.RETRY

            if status_code is not None and 500 <= status_code <= 599:
                return XTFuturesRetryDecision.RETRY

            return XTFuturesRetryDecision.NO_RETRY

        return XTFuturesRetryDecision.NO_RETRY
