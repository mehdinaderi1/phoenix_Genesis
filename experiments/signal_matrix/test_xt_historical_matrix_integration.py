from unittest.mock import patch

from analysis.timeframe_analyzer import TimeframeAnalyzer
from core.database import DatabaseManager
from core.market_data.pipeline import MarketDataPipeline
from exchanges.xt_exchange import XTExchange
from experiments.signal_matrix.market_data_probe import MarketDataMatrixProbe
from market.market_data_reader import MarketDataReader


def test_xt_historical_candles_flow_into_signal_matrix(tmp_path):
    database = DatabaseManager(str(tmp_path / "matrix_probe.db"))
    database.connect()

    try:
        exchange = XTExchange(timeout=5)
        pipeline = MarketDataPipeline(exchange, database)
        reader = MarketDataReader(database)
        analyzer = TimeframeAnalyzer()

        def fake_request(path, params=None):
            interval = params["interval"]
            step_ms = {
                "5m": 5 * 60 * 1000,
                "15m": 15 * 60 * 1000,
            }[interval]

            base_timestamp = 1700000000000
            candles = []

            for index in range(50):
                price = 100 + index
                candles.append({
                    "t": base_timestamp + index * step_ms,
                    "o": str(price),
                    "h": str(price + 1),
                    "l": str(price - 1),
                    "c": str(price + 0.5),
                    "v": str(1000 + index),
                })

            return {"result": list(reversed(candles))}

        with patch.object(exchange, "_request", side_effect=fake_request):
            for timeframe in ("5m", "15m"):
                stored = pipeline.fetch_and_store_historical(
                    symbol="BTCUSDT",
                    timeframe=timeframe,
                    limit=50,
                )
                assert len(stored) == 50

            matrix = MarketDataMatrixProbe(
                reader, analyzer
            ).run(
                symbol="BTCUSDT",
                timeframes=("5m", "15m"),
            )

        records = matrix.all_signals()

        assert len(records) == 2
        assert [record.timeframe for record in records] == ["5m", "15m"]
        assert all(record.state in {
            "BUY", "SELL", "NO_SIGNAL", "NOT_EVALUATED", "DATA_ERROR"
        } for record in records)
        assert all(record.confidence is not None for record in records)
        assert all(record.data_valid for record in records)

    finally:
        database.close()
