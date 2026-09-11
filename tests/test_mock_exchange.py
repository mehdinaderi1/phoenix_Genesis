from exchanges.mock_exchange import MockExchange


def test_mock_exchange_returns_sequenced_prices():
    exchange = MockExchange()

    exchange.set_price_sequence(
        "BTCUSDT",
        [65000.0, 65500.0, 66000.0]
    )

    assert exchange.get_price("BTCUSDT") == 65000.0
    assert exchange.get_price("BTCUSDT") == 65500.0
    assert exchange.get_price("BTCUSDT") == 66000.0


def test_mock_exchange_keeps_last_price_after_sequence():
    exchange = MockExchange()

    exchange.set_price_sequence(
        "BTCUSDT",
        [65000.0, 65500.0, 66000.0]
    )

    assert exchange.get_price("BTCUSDT") == 65000.0
    assert exchange.get_price("BTCUSDT") == 65500.0
    assert exchange.get_price("BTCUSDT") == 66000.0
    assert exchange.get_price("BTCUSDT") == 66000.0


def test_mock_exchange_can_reset_price_sequence():
    exchange = MockExchange()

    exchange.set_price_sequence(
        "BTCUSDT",
        [65000.0, 65500.0, 66000.0]
    )

    assert exchange.get_price("BTCUSDT") == 65000.0
    assert exchange.get_price("BTCUSDT") == 65500.0

    exchange.reset_price_sequences()

    assert exchange.get_price("BTCUSDT") == 65000.0
