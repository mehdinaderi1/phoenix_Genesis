from execution.xt_futures_attempt_state import XTFuturesAttemptState
from execution.xt_futures_attempt_state_resolver import (
    XTFuturesAttemptStateResolver,
)
from execution.xt_futures_error_classifier import (
    XTFuturesErrorClassifier,
)
from execution.xt_futures_response_normalizer import (
    XTFuturesResponseNormalizer,
)
from execution.xt_futures_retry_policy import (
    XTFuturesRetryDecision,
    XTFuturesRetryPolicy,
)


class XTFuturesRetryExecutor:
    """
    Executes retry attempts through an injected transport callable.

    The executor coordinates existing contracts. It does not
    create orders, signatures, or HTTP requests.
    """

    def __init__(
        self,
        classifier=None,
        retry_policy=None,
        state_resolver=None,
        normalizer=None,
    ):
        self.classifier = (
            classifier or XTFuturesErrorClassifier()
        )
        self.retry_policy = (
            retry_policy or XTFuturesRetryPolicy()
        )
        self.state_resolver = (
            state_resolver
            or XTFuturesAttemptStateResolver()
        )
        self.normalizer = (
            normalizer or XTFuturesResponseNormalizer()
        )

    def execute(
        self,
        transport,
        idempotency_key,
        max_attempts=3,
    ):
        if not callable(transport):
            raise TypeError(
                "transport must be callable"
            )

        if not idempotency_key:
            raise ValueError(
                "idempotency_key is required"
            )

        if max_attempts <= 0:
            raise ValueError(
                "max_attempts must be greater than zero"
            )

        attempts = []

        for attempt_number in range(
            1,
            max_attempts + 1
        ):
            try:
                raw_response = transport()
                response = self.normalizer.normalize(
                    raw_response
                )

                error_type = self.classifier.classify(
                    response
                )

                decision = self.retry_policy.decide(
                    error_type=error_type,
                    status_code=response.status_code,
                )

                result = self.state_resolver.resolve(
                    idempotency_key=idempotency_key,
                    error_type=error_type,
                    status_code=response.status_code,
                    error=response.error,
                )

                attempts.append({
                    "attempt": attempt_number,
                    "state": result.state,
                    "error": result.error,
                })

            except (TimeoutError, OSError) as exc:
                error_type = (
                    self.classifier.classify_exception(
                        exc
                    )
                )

                decision = self.retry_policy.decide(
                    error_type=error_type
                )

                result = self.state_resolver.resolve(
                    idempotency_key=idempotency_key,
                    error_type=error_type,
                    error=str(exc),
                )

                attempts.append({
                    "attempt": attempt_number,
                    "state": result.state,
                    "error": result.error,
                })

            if (
                decision == XTFuturesRetryDecision.RETRY
                and attempt_number < max_attempts
            ):
                continue

            return {
                "state": attempts[-1]["state"],
                "attempts": attempts,
            }

        return {
            "state": XTFuturesAttemptState.UNKNOWN,
            "attempts": attempts,
        }
