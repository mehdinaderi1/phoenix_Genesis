from core.database import DatabaseManager
from core.market_data.cross_source_validation_pipeline import CrossSourceValidationPipeline
from core.market_data.cross_source_validator import CrossSourceValidator
from core.market_data.operational_intelligence_runtime import OperationalIntelligenceRuntime
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime
from core.market_data.source_manager import MarketDataSourceManager


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


class FakeIntelligenceFlow:
    def __init__(self):
        self.calls = 0

    def create_report(self, consensus):
        self.calls += 1
        raise AssertionError("Intelligence must not run for SUSPECT data")


class RecordingMarketContextRuntime:
    def __init__(self, results):
        self.results = results
        self.calls = 0

    def run(self, symbol="BTCUSDT", cycles=1):
        self.calls += 1
        return self.results


def test_suspect_market_data_stops_before_intelligence(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    manager = MarketDataSourceManager({
        "binance": FakeSource(65000.0),
        "coinmarketcap": FakeSource(68000.0),
    })

    validator = CrossSourceValidator(max_difference_percent=1.0)
    validation_pipeline = CrossSourceValidationPipeline(
        manager,
        validator
    )

    market_runtime = OperationalMarketContextRuntime(
        database=database,
        validation_pipeline=validation_pipeline
    )

    intelligence = FakeIntelligenceFlow()
    runtime = OperationalIntelligenceRuntime(
        market_context_runtime=market_runtime,
        intelligence_flow=intelligence
    )

    results = runtime.run(symbol="BTCUSDT", cycles=1)

    assert results == []
    assert intelligence.calls == 0

    database.close()
