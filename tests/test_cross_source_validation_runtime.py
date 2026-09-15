from core.database import DatabaseManager
from core.market_data.cross_source_validation_pipeline import CrossSourceValidationPipeline
from core.market_data.cross_source_validator import CrossSourceValidator
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime
from core.market_data.source_manager import MarketDataSourceManager
from core.market_data.validated_market_context_pipeline import ValidatedMarketContextPipeline


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


class FakeValidatedContextRuntime:
    def __init__(self, context):
        self.context = context
        self.calls = 0

    def run(self, symbol="BTCUSDT", cycles=1, timeframes=None):
        self.calls += 1
        if self.context is None:
            return []
        return [self.context]


def build_validation_pipeline(binance_price, cmc_price):
    manager = MarketDataSourceManager({
        "binance": FakeSource(binance_price),
        "coinmarketcap": FakeSource(cmc_price),
    })
    validator = CrossSourceValidator(max_difference_percent=1.0)
    return CrossSourceValidationPipeline(manager, validator)


def test_runtime_accepts_validated_market_context(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    validation_pipeline = build_validation_pipeline(65000.0, 65020.0)
    validated_pipeline = ValidatedMarketContextPipeline(
        database,
        validation_pipeline
    )

    result = validated_pipeline.build("BTCUSDT")

    assert result["validation"].status == "VALID"
    assert result["context"] is not None

    database.close()


def test_runtime_blocks_suspect_market_context(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    validation_pipeline = build_validation_pipeline(65000.0, 68000.0)
    validated_pipeline = ValidatedMarketContextPipeline(
        database,
        validation_pipeline
    )

    result = validated_pipeline.build("BTCUSDT")

    assert result["validation"].status == "SUSPECT"
    assert result["context"] is None

    database.close()
