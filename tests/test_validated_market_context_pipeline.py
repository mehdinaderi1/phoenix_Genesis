from core.database import DatabaseManager
from core.market_data.cross_source_validation_pipeline import CrossSourceValidationPipeline
from core.market_data.cross_source_validator import CrossSourceValidator
from core.market_data.source_manager import MarketDataSourceManager
from core.market_data.validated_market_context_pipeline import ValidatedMarketContextPipeline
from exchanges.mock_exchange import MockExchange


class FakeSource:
    def __init__(self, price, healthy=True):
        self.price = price
        self.healthy = healthy

    def health_check(self):
        return self.healthy

    def connect(self):
        return True

    def get_price(self, symbol):
        return self.price


def build_pipeline(database, binance_price, cmc_price, cmc_healthy=True):
    manager = MarketDataSourceManager({
        "binance": FakeSource(binance_price),
        "coinmarketcap": FakeSource(cmc_price, cmc_healthy),
    })
    validator = CrossSourceValidator(max_difference_percent=1.0)
    validation_pipeline = CrossSourceValidationPipeline(
        manager,
        validator
    )
    return ValidatedMarketContextPipeline(
        database,
        validation_pipeline
    )


def seed_market_data(database):
    for timeframe in ("30m", "4H", "1D"):
        for index, price in enumerate([65000.0] * 5):
            database.connection.execute(
                "INSERT INTO market_candles "
                "(symbol, timeframe, timestamp, open, high, low, close, volume) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    "BTCUSDT",
                    timeframe,
                    index + 1,
                    price,
                    price + 100.0,
                    price - 100.0,
                    price,
                    10.0
                )
            )
    database.connection.commit()


def test_validated_pipeline_allows_valid_market_context(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()
    seed_market_data(database)

    pipeline = build_pipeline(database, 65000.0, 65020.0)

    result = pipeline.build("BTCUSDT")

    assert result["validation"].status == "VALID"
    assert result["context"] is not None
    assert result["context"].symbol == "BTCUSDT"

    database.close()


def test_validated_pipeline_blocks_suspect_market_context(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()
    seed_market_data(database)

    pipeline = build_pipeline(database, 65000.0, 68000.0)

    result = pipeline.build("BTCUSDT")

    assert result["validation"].status == "SUSPECT"
    assert result["context"] is None

    database.close()


def test_validated_pipeline_allows_insufficient_market_context(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()
    seed_market_data(database)

    pipeline = build_pipeline(
        database,
        65000.0,
        65020.0,
        cmc_healthy=False
    )

    result = pipeline.build("BTCUSDT")

    assert result["validation"].status == "INSUFFICIENT"
    assert result["context"] is not None

    database.close()


def test_validated_pipeline_blocks_blind_market_context(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()
    seed_market_data(database)

    pipeline = build_pipeline(
        database,
        65000.0,
        65020.0,
        cmc_healthy=False
    )

    pipeline.validation_pipeline.source_manager.sources["binance"].healthy = False

    result = pipeline.build("BTCUSDT")

    assert result["validation"].status == "BLIND"
    assert result["context"] is None

    database.close()
