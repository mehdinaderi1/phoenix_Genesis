from execution.paper_position import PaperPosition
from execution.paper_trade_history import PaperTradeHistory


def test_add_closed_trade_to_history():

    position = PaperPosition(
        symbol="BTCUSDT",
        side="BUY",
        entry_price=65000,
        quantity=0.01
    )

    history = PaperTradeHistory()

    record = history.add_trade(
        position=position,
        exit_price=66000,
        realized_pnl=10
    )

    assert record.symbol == "BTCUSDT"
    assert record.side == "BUY"
    assert record.entry_price == 65000
    assert record.exit_price == 66000
    assert record.quantity == 0.01
    assert record.realized_pnl == 10


def test_trade_history_counts_trades():

    history = PaperTradeHistory()

    position = PaperPosition(
        symbol="BTCUSDT",
        side="BUY",
        entry_price=65000,
        quantity=0.01
    )

    history.add_trade(
        position,
        66000,
        10
    )

    history.add_trade(
        position,
        64000,
        -10
    )

    assert history.get_trade_count() == 2


def test_trade_history_calculates_total_realized_pnl():

    history = PaperTradeHistory()

    position = PaperPosition(
        symbol="BTCUSDT",
        side="BUY",
        entry_price=65000,
        quantity=0.01
    )

    history.add_trade(
        position,
        66000,
        10
    )

    history.add_trade(
        position,
        64000,
        -10
    )

    history.add_trade(
        position,
        67000,
        20
    )

    assert history.get_total_realized_pnl() == 20


def test_empty_history():

    history = PaperTradeHistory()

    assert history.get_trade_count() == 0
    assert history.get_total_realized_pnl() == 0
    assert history.get_trades() == []