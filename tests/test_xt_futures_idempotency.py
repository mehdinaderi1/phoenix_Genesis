import pytest

from execution.xt_futures_idempotency import (
    XTFuturesIdempotencyKey,
    XTFuturesIdempotencyKeyBuilder,
)


@pytest.fixture
def builder():
    return XTFuturesIdempotencyKeyBuilder()


def test_same_order_produces_same_key(builder):
    first = builder.build(
        symbol="BTCUSDT",
        order_side="BUY",
        position_side="LONG",
        order_type="MARKET",
        quantity=0.001,
    )

    second = builder.build(
        symbol="BTCUSDT",
        order_side="BUY",
        position_side="LONG",
        order_type="MARKET",
        quantity=0.001,
    )

    assert first == second
    assert first.value == second.value


def test_key_is_sha256_hex(builder):
    key = builder.build(
        symbol="BTCUSDT",
        order_side="BUY",
        position_side="LONG",
        order_type="MARKET",
        quantity=0.001,
    )

    assert isinstance(key, XTFuturesIdempotencyKey)
    assert len(key.value) == 64
    assert all(
        char in "0123456789abcdef"
        for char in key.value
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("symbol", "ETHUSDT"),
        ("order_side", "SELL"),
        ("position_side", "SHORT"),
        ("order_type", "LIMIT"),
        ("quantity", 0.002),
        ("price", 60000),
    ],
)
def test_order_defining_change_changes_key(
    builder,
    field,
    value,
):
    base = {
        "symbol": "BTCUSDT",
        "order_side": "BUY",
        "position_side": "LONG",
        "order_type": "MARKET",
        "quantity": 0.001,
        "price": None,
    }

    changed = dict(base)
    changed[field] = value

    first = builder.build(**base)
    second = builder.build(**changed)

    assert first != second


def test_none_price_is_deterministic(builder):
    first = builder.build(
        symbol="BTCUSDT",
        order_side="BUY",
        position_side="LONG",
        order_type="MARKET",
        quantity=0.001,
        price=None,
    )

    second = builder.build(
        symbol="BTCUSDT",
        order_side="BUY",
        position_side="LONG",
        order_type="MARKET",
        quantity=0.001,
        price=None,
    )

    assert first == second


def test_key_changes_when_price_is_added(builder):
    market = builder.build(
        symbol="BTCUSDT",
        order_side="BUY",
        position_side="LONG",
        order_type="MARKET",
        quantity=0.001,
    )

    priced = builder.build(
        symbol="BTCUSDT",
        order_side="BUY",
        position_side="LONG",
        order_type="MARKET",
        quantity=0.001,
        price=65000,
    )

    assert market != priced


def test_invalid_empty_key_is_rejected():
    with pytest.raises(
        ValueError,
        match="idempotency key is required",
    ):
        XTFuturesIdempotencyKey("")
