from execution.xt_futures_order_confirmation import (
    XTFuturesOrderConfirmationState,
)
from execution.xt_futures_order_confirmation_interpreter import (
    XTFuturesOrderConfirmationInterpreter,
)
from execution.xt_futures_response import XTFuturesResponse


def make_response(state, order_id="123"):
    return XTFuturesResponse(
        status_code=200,
        ok=True,
        body={
            "result": {
                "orderId": order_id,
                "state": state,
            }
        },
        raw_body="{}",
    )


def test_filled_order_is_confirmed():
    result = XTFuturesOrderConfirmationInterpreter().interpret(
        make_response("FILLED")
    )

    assert result.state == (
        XTFuturesOrderConfirmationState.CONFIRMED
    )
    assert result.order_id == "123"


def test_new_order_is_unknown():
    result = XTFuturesOrderConfirmationInterpreter().interpret(
        make_response("NEW")
    )

    assert result.state == (
        XTFuturesOrderConfirmationState.UNKNOWN
    )
    assert result.order_id == "123"


def test_partially_filled_order_is_unknown():
    result = XTFuturesOrderConfirmationInterpreter().interpret(
        make_response("PARTIALLY_FILLED")
    )

    assert result.state == (
        XTFuturesOrderConfirmationState.UNKNOWN
    )


def test_partially_canceled_order_is_unknown():
    result = XTFuturesOrderConfirmationInterpreter().interpret(
        make_response("PARTIALLY_CANCELED")
    )

    assert result.state == (
        XTFuturesOrderConfirmationState.UNKNOWN
    )


def test_canceled_order_is_rejected():
    result = XTFuturesOrderConfirmationInterpreter().interpret(
        make_response("CANCELED")
    )

    assert result.state == (
        XTFuturesOrderConfirmationState.REJECTED
    )


def test_rejected_order_is_rejected():
    result = XTFuturesOrderConfirmationInterpreter().interpret(
        make_response("REJECTED")
    )

    assert result.state == (
        XTFuturesOrderConfirmationState.REJECTED
    )


def test_expired_order_is_rejected():
    result = XTFuturesOrderConfirmationInterpreter().interpret(
        make_response("EXPIRED")
    )

    assert result.state == (
        XTFuturesOrderConfirmationState.REJECTED
    )


def test_missing_result_is_unknown():
    response = XTFuturesResponse(
        status_code=200,
        ok=True,
        body={},
        raw_body="{}",
    )

    result = XTFuturesOrderConfirmationInterpreter().interpret(
        response
    )

    assert result.state == (
        XTFuturesOrderConfirmationState.UNKNOWN
    )


def test_missing_state_is_unknown():
    response = XTFuturesResponse(
        status_code=200,
        ok=True,
        body={
            "result": {
                "orderId": "123",
            }
        },
        raw_body="{}",
    )

    result = XTFuturesOrderConfirmationInterpreter().interpret(
        response
    )

    assert result.state == (
        XTFuturesOrderConfirmationState.UNKNOWN
    )


def test_missing_order_id_is_unknown():
    response = XTFuturesResponse(
        status_code=200,
        ok=True,
        body={
            "result": {
                "state": "FILLED",
            }
        },
        raw_body="{}",
    )

    result = XTFuturesOrderConfirmationInterpreter().interpret(
        response
    )

    assert result.state == (
        XTFuturesOrderConfirmationState.UNKNOWN
    )


def test_http_failure_remains_unknown():
    response = XTFuturesResponse(
        status_code=500,
        ok=False,
        body={"error": "server error"},
        raw_body="{}",
        error="HTTP 500",
    )

    result = XTFuturesOrderConfirmationInterpreter().interpret(
        response
    )

    assert result.state == (
        XTFuturesOrderConfirmationState.UNKNOWN
    )
