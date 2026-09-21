from core.database import DatabaseManager
from core.market_data.operational_market_context_runtime import (
    OperationalMarketContextRuntime
)


class FakeSourceCandlePipeline:

    def __init__(self):
        self.calls = []

    def fetch_and_store(self, symbol, timeframe):
        self.calls.append((symbol, timeframe))
        return {
            "stored": True,
            "source": "fake",
            "candle": {
                "timestamp": len(self.calls),
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.5,
                "volume": 10.0,
            },
        }


def test_operational_runtime_accepts_lower_timeframes(tmp_path):
    database = DatabaseManager(
        db_path=str(tmp_path / "phoenix.db")
    )
    database.connect()

    pipeline = FakeSourceCandlePipeline()

    runtime = OperationalMarketContextRuntime(
        database=database,
        source_candle_pipeline=pipeline
    )

    result = runtime.run_cycle(
        symbol="BTCUSDT",
        timeframes=("5m", "15m")
    )

    assert result["context"] is not None

    assert pipeline.calls == [
        ("BTCUSDT", "5m"),
        ("BTCUSDT", "15m")
    ]

    database.close()
