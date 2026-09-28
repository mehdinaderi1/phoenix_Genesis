import pytest

from execution.xt_futures_order_confirmation import (
    XTFuturesOrderConfirmation,
    XTFuturesOrderConfirmationState,
)
from execution.xt_futures_order_confirmation_interpreter import (
    XTFuturesOrderConfirmationInterpreter,
)
from execution.xt_futures_response import XTFuturesResponse


def test_confirmed_requires_order_id():
    with pytest.raises(
        ValueError,
        match="CONFIRMED order requires order_id",
    ):
        XTFuturesOrderConfirmation(
            state=XTFuturesOrderConfirmationState.CONFIRMED
        )


def test_rejected_requires_error():
    with pytest.raises(
        ValueError,
        match="REJECTED order requires error",
    ):
        XTFuturesOrderConfirmation(
            state=XTFuturesOrderConfirmationState.REJECTED
        )


def test_interpreter_does_not_treat_http_200_as_confirmed():
    response = XTFuturesResponse(
        status_code=200,
        ok=True,
        body={"result": {"orderId": "123"}},
        raw_body='{"result":{"orderId":"123"}}',
    )

    result = XTFuturesOrderConfirmationInterpreter().interpret(
        response
    )

    assert result.state == (
        XTFuturesOrderConfirmationState.UNKNOWN
    )
    assert result.order_id is None


def test_interpreter_rejects_failed_http_response():
    response = XTFuturesResponse(
        status_code=400,
        ok=False,
        body={"error": "bad request"},
        raw_body='{"error":"bad request"}',
        error="HTTP 400",
    )

    result = XTFuturesOrderConfirmationInterpreter().interpret(
        response
    )

    assert result.state == (
        XTFuturesOrderConfirmationState.UNKNOWN
    )
    assert result.error == "HTTP 400"


def test_interpreter_requires_response():
    with pytest.raises(
        TypeError,
        match="response is required",
    ):
        XTFuturesOrderConfirmationInterpreter().interpret(
            None
        )
