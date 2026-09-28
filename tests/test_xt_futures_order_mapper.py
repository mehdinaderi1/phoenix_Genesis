from dataclasses import dataclass

import pytest

from execution.xt_futures_order_mapper import (
    XTFuturesOrderMapper
)


@dataclass
class FakeActionProposal:
    action: str
    symbol: str = "BTCUSDT"


@dataclass
class FakePosition:
    side: str


@pytest.fixture
def mapper():
    return XTFuturesOrderMapper()


def test_flat_buy_opens_long(mapper):
    request = mapper.build(
        FakeActionProposal("BUY"),
        position=None,
        quantity=0.001
    )

    assert request.order_side == "BUY"
    assert request.position_side == "LONG"
    assert request.order_type == "MARKET"
    assert request.quantity == 0.001


def test_flat_sell_opens_short(mapper):
    request = mapper.build(
        FakeActionProposal("SELL"),
        position=None,
        quantity=0.001
    )

    assert request.order_side == "SELL"
    assert request.position_side == "SHORT"


def test_long_sell_closes_long(mapper):
    request = mapper.build(
        FakeActionProposal("SELL"),
        position=FakePosition("BUY"),
        quantity=0.001
    )

    assert request.order_side == "SELL"
    assert request.position_side == "LONG"


def test_short_buy_closes_short(mapper):
    request = mapper.build(
        FakeActionProposal("BUY"),
        position=FakePosition("SELL"),
        quantity=0.001
    )

    assert request.order_side == "BUY"
    assert request.position_side == "SHORT"


def test_same_side_buy_returns_no_order(mapper):
    request = mapper.build(
        FakeActionProposal("BUY"),
        position=FakePosition("BUY"),
        quantity=0.001
    )

    assert request is None


def test_same_side_sell_returns_no_order(mapper):
    request = mapper.build(
        FakeActionProposal("SELL"),
        position=FakePosition("SELL"),
        quantity=0.001
    )

    assert request is None


def test_wait_returns_no_order(mapper):
    request = mapper.build(
        FakeActionProposal("WAIT"),
        position=None,
        quantity=0.001
    )

    assert request is None


def test_quantity_is_required(mapper):
    with pytest.raises(ValueError, match="quantity is required"):
        mapper.build(
            FakeActionProposal("BUY"),
            position=None
        )


def test_position_side_is_not_mutated(mapper):
    position = FakePosition("BUY")

    mapper.build(
        FakeActionProposal("SELL"),
        position=position,
        quantity=0.001
    )

    assert position.side == "BUY"


def test_limit_order_passes_price(mapper):
    request = mapper.build(
        FakeActionProposal("BUY"),
        position=None,
        quantity=0.001,
        order_type="LIMIT",
        price=65000.0
    )

    assert request.order_type == "LIMIT"
    assert request.price == 65000.0
