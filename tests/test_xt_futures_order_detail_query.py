import pytest

from execution.xt_futures_order_detail_query import (
    XTFuturesOrderDetailQueryBuilder,
)


def test_builder_creates_order_detail_request():
    request = XTFuturesOrderDetailQueryBuilder().build(1234567890)

    assert request.order_id == 1234567890


def test_request_exposes_xt_query_parameter():
    request = XTFuturesOrderDetailQueryBuilder().build(1234567890)

    assert request.to_query_params() == {
        "orderId": 1234567890,
    }


def test_endpoint_is_verified_xt_endpoint():
    assert (
        XTFuturesOrderDetailQueryBuilder.ENDPOINT
        == "/future/trade/v1/order/detail"
    )


def test_order_id_must_be_integer():
    with pytest.raises(ValueError):
        XTFuturesOrderDetailQueryBuilder().build("1234567890")


def test_order_id_must_be_positive():
    with pytest.raises(ValueError):
        XTFuturesOrderDetailQueryBuilder().build(0)


def test_negative_order_id_is_rejected():
    with pytest.raises(ValueError):
        XTFuturesOrderDetailQueryBuilder().build(-1)


def test_boolean_order_id_is_rejected():
    with pytest.raises(ValueError):
        XTFuturesOrderDetailQueryBuilder().build(True)
