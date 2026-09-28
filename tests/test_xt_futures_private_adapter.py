from exchanges.xt_futures_private_adapter import XTFuturesPrivateAdapter


def test_xt_futures_signature_generation():
    adapter = XTFuturesPrivateAdapter(
        appkey="test-appkey",
        secret_key="test-secret",
    )

    signature = adapter.generate_signature(
        timestamp=1700000000000,
        endpoint="/future/user/v1/compat/balance/list",
        query_string="queryAccountId=1234567890",
    )

    assert signature == (
        "5a110034b43ab3113241fed86f8ff5dce43bfb0058320e9fce0a4dff538139f5"
    )


def test_build_query_string_sorts_parameters():
    adapter = XTFuturesPrivateAdapter("test-appkey", "test-secret")

    query_string = adapter.build_query_string(
        {"symbol": "BTCUSDT", "limit": 100, "timestamp": 1700000000000}
    )

    assert query_string == "limit=100&symbol=BTCUSDT&timestamp=1700000000000"


def test_build_query_string_is_independent_of_input_order():
    adapter = XTFuturesPrivateAdapter("test-appkey", "test-secret")

    first = adapter.build_query_string(
        {"symbol": "BTCUSDT", "limit": 100}
    )
    second = adapter.build_query_string(
        {"limit": 100, "symbol": "BTCUSDT"}
    )

    assert first == second


def test_build_query_string_preserves_parameter_values():
    adapter = XTFuturesPrivateAdapter("test-appkey", "test-secret")

    query_string = adapter.build_query_string(
        {"symbol": "BTC USDT", "side": "BUY"}
    )

    assert query_string == "side=BUY&symbol=BTC+USDT"
from exchanges.xt_futures_private_adapter import (
    XTFuturesPrivateAdapter
)


def test_generate_signature_for_request_body():
    adapter = XTFuturesPrivateAdapter(
        appkey="APPKEY",
        secret_key="SECRET"
    )

    signature = adapter.generate_body_signature(
        timestamp="1234567890",
        endpoint="/future/trade/v1/order/create",
        request_body='{"symbol":"btc_usdt","origQty":1}'
    )

    assert isinstance(signature, str)
    assert len(signature) == 64


def test_body_signature_is_deterministic():
    adapter = XTFuturesPrivateAdapter(
        appkey="APPKEY",
        secret_key="SECRET"
    )

    first = adapter.generate_body_signature(
        timestamp="1234567890",
        endpoint="/future/trade/v1/order/create",
        request_body='{"symbol":"btc_usdt","origQty":1}'
    )

    second = adapter.generate_body_signature(
        timestamp="1234567890",
        endpoint="/future/trade/v1/order/create",
        request_body='{"symbol":"btc_usdt","origQty":1}'
    )

    assert first == second


def test_body_signature_changes_when_body_changes():
    adapter = XTFuturesPrivateAdapter(
        appkey="APPKEY",
        secret_key="SECRET"
    )

    first = adapter.generate_body_signature(
        timestamp="1234567890",
        endpoint="/future/trade/v1/order/create",
        request_body='{"symbol":"btc_usdt","origQty":1}'
    )

    second = adapter.generate_body_signature(
        timestamp="1234567890",
        endpoint="/future/trade/v1/order/create",
        request_body='{"symbol":"btc_usdt","origQty":2}'
    )

    assert first != second
