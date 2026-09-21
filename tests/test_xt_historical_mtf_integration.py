from unittest.mock import patch

from analysis.timeframe_analyzer import TimeframeAnalyzer
from core.database import DatabaseManager
from core.market_data.pipeline import MarketDataPipeline
from exchanges.xt_exchange import XTExchange
from market.market_data_reader import MarketDataReader


def test_xt_historical_5m_and_15m_flow_to_analyzer(tmp_path):
    database = DatabaseManager(
        str(tmp_path / "test.db")
    )
    database.connect()

    exchange = XTExchange(timeout=5)
    pipeline = MarketDataPipeline(
        exchange,
        database
    )
    reader = MarketDataReader(database)
    analyzer = TimeframeAnalyzer()

    def fake_request(path, params=None):
        interval = params["interval"]

        base_timestamp = 1700000000000

        if interval == "5m":
            step = 5 * 60 * 1000
        else:
            step = 15 * 60 * 1000

        candles = []

        for index in range(50):
            timestamp = base_timestamp + index * step
            price = 100 + index

            candles.append(
                {
                    "t": timestamp,
                    "o": str(price),
                    "h": str(price + 1),
                    "l": str(price - 1),
                    "c": str(price + 0.5),
                    "v": str(1000 + index),
                }
            )

        return {
            "result": list(reversed(candles))
        }

    with patch.object(
        exchange,
        "_request",
        side_effect=fake_request
    ):
        for timeframe in ("5m", "15m"):

            stored = pipeline.fetch_and_store_historical(
                symbol="BTCUSDT",
                timeframe=timeframe,
                limit=50
            )

            assert len(stored) == 50

            assert (
                stored[0]["timestamp"]
                < stored[-1]["timestamp"]
            )

            prices = reader.get_close_prices(
                "BTCUSDT",
                timeframe
            )

            assert len(prices) == 50

            result = analyzer.analyze(
                prices,
                timeframe
            )

            assert result is not None
            assert result.trend in {
                "BULLISH",
                "BEARISH",
                "NEUTRAL"
            }
            assert result.signal in {
                "BUY",
                "SELL",
                "WAIT"
            }
            assert 0 <= result.confidence <= 100

    database.close()
