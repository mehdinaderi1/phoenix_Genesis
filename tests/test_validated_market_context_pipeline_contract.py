from core.database import DatabaseManager
from core.market_data.cross_source_validation_pipeline import CrossSourceValidationPipeline
from core.market_data.operational_market_context import OperationalMarketContext
from core.market_data.validated_market_context import ValidatedMarketContext
from core.market_data.validated_market_context_pipeline import ValidatedMarketContextPipeline


class FakeSource:
    def __init__(self, price, healthy=True):
        self.price = price
        self.healthy = healthy

    def health_check(self):
        return self.healthy

    def get_price(self, symbol):
        return self.price


def test_validated_market_context_pipeline_returns_validated_context(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    sources = {
        "binance": FakeSource(65000.0),
        "coinmarketcap": FakeSource(65020.0),
    }

    from core.market_data.source_manager import MarketDataSourceManager

    manager = MarketDataSourceManager(sources)

    validation_pipeline = CrossSourceValidationPipeline(manager)

    pipeline = ValidatedMarketContextPipeline(
        database=database,
        validation_pipeline=validation_pipeline,
    )

    class FakeContextPipeline:
        def build(self, symbol):
            return OperationalMarketContext(
                symbol=symbol,
                trend="BULLISH",
                signal="BUY",
                confidence=85.0,
                timestamp="2026-01-01T00:00:00+00:00",
            )

    pipeline.context_pipeline = FakeContextPipeline()

    result = pipeline.build("BTCUSDT")

    assert isinstance(result["context"], ValidatedMarketContext)
    assert result["validation"].status == "VALID"
    assert result["context"].context.symbol == "BTCUSDT"
    assert result["context"].validation.status == "VALID"

    database.close()
