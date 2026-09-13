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


def test_mock_exchange_returns_sequenced_candles():
    exchange = MockExchange()

    candles = [
        {
            "timestamp": 1752364800,
            "open": 64950,
            "high": 65100,
            "low": 64800,
            "close": 65000,
            "volume": 125.5
        },
        {
            "timestamp": 1752364860,
            "open": 65450,
            "high": 65600,
            "low": 65300,
            "close": 65500,
            "volume": 130.0
        },
        {
            "timestamp": 1752364920,
            "open": 65950,
            "high": 66100,
            "low": 65800,
            "close": 66000,
            "volume": 135.0
        }
    ]

    exchange.set_candle_sequence(
        "BTCUSDT",
        "1m",
        candles
    )

    assert exchange.get_candle("BTCUSDT", "1m") == candles[0]
    assert exchange.get_candle("BTCUSDT", "1m") == candles[1]
    assert exchange.get_candle("BTCUSDT", "1m") == candles[2]


def test_mock_exchange_keeps_last_candle_after_sequence():
    exchange = MockExchange()

    candles = [
        {
            "timestamp": 1752364800,
            "open": 64950,
            "high": 65100,
            "low": 64800,
            "close": 65000,
            "volume": 125.5
        },
        {
            "timestamp": 1752364860,
            "open": 65450,
            "high": 65600,
            "low": 65300,
            "close": 65500,
            "volume": 130.0
        }
    ]

    exchange.set_candle_sequence(
        "BTCUSDT",
        "1m",
        candles
    )

    assert exchange.get_candle("BTCUSDT", "1m") == candles[0]
    assert exchange.get_candle("BTCUSDT", "1m") == candles[1]
    assert exchange.get_candle("BTCUSDT", "1m") == candles[1]


def test_mock_exchange_can_reset_candle_sequence():
    exchange = MockExchange()

    candles = [
        {
            "timestamp": 1752364800,
            "open": 64950,
            "high": 65100,
            "low": 64800,
            "close": 65000,
            "volume": 125.5
        },
        {
            "timestamp": 1752364860,
            "open": 65450,
            "high": 65600,
            "low": 65300,
            "close": 65500,
            "volume": 130.0
        }
    ]

    exchange.set_candle_sequence(
        "BTCUSDT",
        "1m",
        candles
    )

    assert exchange.get_candle("BTCUSDT", "1m") == candles[0]
    assert exchange.get_candle("BTCUSDT", "1m") == candles[1]

    exchange.reset_candle_sequences()

    assert exchange.get_candle("BTCUSDT", "1m") == candles[0]
