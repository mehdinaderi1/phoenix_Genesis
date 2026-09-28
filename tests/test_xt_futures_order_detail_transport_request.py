from execution.xt_futures_order_detail_query import (
    XTFuturesOrderDetailQueryBuilder,
)
from exchanges.xt_futures_private_adapter import XTFuturesPrivateAdapter
from execution.xt_futures_transport_request import XTFuturesTransportRequest


def test_order_detail_query_string_uses_xt_parameter_name():
    request = XTFuturesOrderDetailQueryBuilder().build(1234567890)

    adapter = XTFuturesPrivateAdapter("app-key", "secret")

    query_string = adapter.build_query_string(
        request.to_query_params()
    )

    assert query_string == "orderId=1234567890"


def test_order_detail_signature_is_generated_from_endpoint_and_query():
    request = XTFuturesOrderDetailQueryBuilder().build(1234567890)

    adapter = XTFuturesPrivateAdapter("app-key", "secret")

    query_string = adapter.build_query_string(
        request.to_query_params()
    )

    signature = adapter.generate_signature(
        timestamp="1700000000000",
        endpoint="/future/trade/v1/order/detail",
        query_string=query_string,
    )

    assert isinstance(signature, str)
    assert len(signature) == 64


def test_order_detail_transport_request_contains_signed_get_identity():
    request = XTFuturesOrderDetailQueryBuilder().build(1234567890)

    adapter = XTFuturesPrivateAdapter("app-key", "secret")

    query_string = adapter.build_query_string(
        request.to_query_params()
    )

    signature = adapter.generate_signature(
        timestamp="1700000000000",
        endpoint="/future/trade/v1/order/detail",
        query_string=query_string,
    )

    transport_request = XTFuturesTransportRequest(
        endpoint=(
            "https://fapi.xt.com"
            "/future/trade/v1/order/detail?"
            + query_string
        ),
        body="",
        timestamp="1700000000000",
        appkey="app-key",
        signature=signature,
    )

    assert transport_request.endpoint == (
        "https://fapi.xt.com"
        "/future/trade/v1/order/detail?"
        "orderId=1234567890"
    )

    headers = transport_request.headers()

    assert headers["validate-appkey"] == "app-key"
    assert headers["validate-timestamp"] == "1700000000000"
    assert headers["validate-signature"] == signature
