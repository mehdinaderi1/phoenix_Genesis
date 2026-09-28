from execution.xt_futures_attempt_state import (
    XTFuturesAttemptState,
)
from execution.xt_futures_confirmation_state_resolver import (
    XTFuturesConfirmationStateResolver,
)
from execution.xt_futures_order_confirmation_interpreter import (
    XTFuturesOrderConfirmationInterpreter,
)
from execution.xt_futures_response import XTFuturesResponse


def test_response_to_attempt_state_keeps_unverified_success_unknown():
    response = XTFuturesResponse(
        status_code=200,
        ok=True,
        body={
            "result": {
                "orderId": "123"
            }
        },
        raw_body='{"result":{"orderId":"123"}}',
    )

    confirmation = (
        XTFuturesOrderConfirmationInterpreter().interpret(
            response
        )
    )

    result = XTFuturesConfirmationStateResolver().resolve(
        idempotency_key="abc123",
        confirmation=confirmation,
    )

    assert result.state == XTFuturesAttemptState.UNKNOWN
    assert result.idempotency_key == "abc123"
