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


class FakeContext:
    symbol = "BTCUSDT"
    trend = "BULLISH"
    signal = "BUY"
    confidence = 85.0
    timestamp = "2026-01-01T00:00:00+00:00"


class RecordingContextPipeline:
    def __init__(self):
        self.calls = 0

    def build(self, symbol):
        self.calls += 1
        return FakeContext()


def build_runtime(tmp_path, status):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    validation_pipeline = FakeValidationPipeline(status)
    runtime = OperationalMarketContextRuntime(
        database=database,
        validation_pipeline=validation_pipeline
    )

    context_pipeline = RecordingContextPipeline()
    runtime.context_pipeline = context_pipeline

    return database, runtime, validation_pipeline, context_pipeline


def test_valid_validation_builds_context(tmp_path):
    database, runtime, validation, context = build_runtime(
        tmp_path, "VALID"
    )

    result = runtime.run_cycle("BTCUSDT")

    assert validation.calls == 1
    assert context.calls == 1
    assert result["validation"].status == "VALID"
    assert result["context"] is not None

    database.close()


def test_insufficient_validation_builds_context(tmp_path):
    database, runtime, validation, context = build_runtime(
        tmp_path, "INSUFFICIENT"
    )

    result = runtime.run_cycle("BTCUSDT")

    assert validation.calls == 1
    assert context.calls == 1
    assert result["validation"].status == "INSUFFICIENT"
    assert result["context"] is not None

    database.close()


def test_suspect_validation_blocks_context_build(tmp_path):
    database, runtime, validation, context = build_runtime(
        tmp_path, "SUSPECT"
    )

    result = runtime.run_cycle("BTCUSDT")

    assert validation.calls == 1
    assert context.calls == 0
    assert result["validation"].status == "SUSPECT"
    assert result["context"] is None

    database.close()


def test_blind_validation_blocks_context_build(tmp_path):
    database, runtime, validation, context = build_runtime(
        tmp_path, "BLIND"
    )

    result = runtime.run_cycle("BTCUSDT")

    assert validation.calls == 1
    assert context.calls == 0
    assert result["validation"].status == "BLIND"
    assert result["context"] is None

    database.close()
