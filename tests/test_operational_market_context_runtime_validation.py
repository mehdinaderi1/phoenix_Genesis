from core.database import DatabaseManager
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime


class FakeValidationResult:
    def __init__(self, status):
        self.status = status


class FakeValidationPipeline:
    def __init__(self, status):
        self.status = status
        self.calls = 0

    def validate(self, symbol):
        self.calls += 1
        return FakeValidationResult(self.status)


class FakeContextPipeline:
    def __init__(self, context=None):
        self.context = context
        self.calls = 0

    def build(self, symbol):
        self.calls += 1
        return self.context


class FakeObserver:
    def observe(self, symbol):
        return type(
            "Observation",
            (),
            {"source_status": "HEALTHY"}
        )()


class FakeMarketDataPipeline:
    def fetch_and_store(self, symbol, timeframe):
        return {
            "timestamp": 1,
            "open": 65000.0,
            "high": 65100.0,
            "low": 64900.0,
            "close": 65000.0,
            "volume": 10.0
        }


def test_runtime_uses_validation_pipeline_before_context(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    runtime = OperationalMarketContextRuntime(
        database=database,
        validation_pipeline=FakeValidationPipeline("VALID")
    )

    assert runtime.validation_pipeline is not None
    assert runtime.validation_pipeline.status == "VALID"

    database.close()


def test_runtime_can_receive_suspect_validation_state(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    runtime = OperationalMarketContextRuntime(
        database=database,
        validation_pipeline=FakeValidationPipeline("SUSPECT")
    )

    assert runtime.validation_pipeline is not None
    assert runtime.validation_pipeline.status == "SUSPECT"

    database.close()
