from core.database import DatabaseManager
from core.market_data.cross_source_validation_pipeline import CrossSourceValidationPipeline
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime
from core.market_data.source_manager import MarketDataSourceManager


class FakeSource:
    def __init__(self, price):
        self.price = price

    def health_check(self):
        return True

    def get_price(self, symbol):
        return self.price


class FailingContextPipeline:
    def __init__(self):
        self.called = False

    def build(self, symbol):
        self.called = True
        raise AssertionError(
            "Market context must not be built for SUSPECT data"
        )


class FailingIntelligenceFlow:
    def create_report(self, consensus):
        raise AssertionError(
            "Intelligence must not run for SUSPECT data"
        )


def test_suspect_validation_stops_before_intelligence(tmp_path):
    database = DatabaseManager(
        db_path=str(tmp_path / "phoenix.db")
    )
    database.connect()

    manager = MarketDataSourceManager(
        {
            "binance": FakeSource(65000.0),
            "coinmarketcap": FakeSource(68000.0),
        }
    )

    validation_pipeline = CrossSourceValidationPipeline(manager)

    runtime = OperationalMarketContextRuntime(
        database=database,
        validation_pipeline=validation_pipeline,
    )

    context_pipeline = FailingContextPipeline()
    runtime.context_pipeline = context_pipeline

    result = runtime.run_cycle("BTCUSDT")

    assert result["validation"].status == "SUSPECT"
    assert result["context"] is None
    assert context_pipeline.called is False

    database.close()
