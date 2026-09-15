from core.database import DatabaseManager
from core.market_data.market_data import MarketData
from core.market_data.observer import RealMarketObserver
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime
from core.market_data.operational_intelligence_runtime import OperationalIntelligenceRuntime
from core.market_data.pipeline import MarketDataPipeline
from core.market_data.source_manager import MarketDataSourceManager
from exchanges.mock_exchange import MockExchange
from intelligence.flow import IntelligenceFlow


class FakeSource:
    def __init__(self, price, healthy=True, name="source"):
        self.price = price
        self.healthy = healthy
        self.name = name

    def connect(self):
        if not self.healthy:
            raise RuntimeError(f"{self.name} unavailable")
        return True

    def health_check(self):
        return self.healthy

    def get_price(self, symbol):
        if not self.healthy:
            raise RuntimeError(f"{self.name} unavailable")
        return self.price


class RecordingIntelligenceFlow(IntelligenceFlow):
    def __init__(self):
        super().__init__()
        self.consensus_history = []
        self.report_history = []

    def create_report(self, consensus):
        self.consensus_history.append(consensus)
        report = super().create_report(consensus)
        self.report_history.append(report)
        return report


def build_runtime(tmp_path, primary, fallback):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    exchange = MockExchange()
    candle = {
        "timestamp": 1001,
        "open": 65000.0,
        "high": 65100.0,
        "low": 64900.0,
        "close": 65000.0,
        "volume": 10.0,
    }

    for timeframe in ("30m", "4H", "1D"):
        exchange.set_candle_sequence(
            "BTCUSDT",
            timeframe,
            [candle]
        )

    pipeline = MarketDataPipeline(exchange, database)

    manager = MarketDataSourceManager({
        "primary": primary,
        "fallback": fallback,
    })
    manager.set_primary_source("primary")

    observer = RealMarketObserver(manager)

    market_runtime = OperationalMarketContextRuntime(
        observer=observer,
        market_data_pipeline=pipeline,
        database=database,
    )

    intelligence_flow = RecordingIntelligenceFlow()

    intelligence_runtime = OperationalIntelligenceRuntime(
        market_context_runtime=market_runtime,
        intelligence_flow=intelligence_flow,
    )

    return database, intelligence_runtime, intelligence_flow, observer


def test_fallback_market_data_reaches_intelligence(tmp_path):
    primary = FakeSource(
        price=65000.0,
        healthy=False,
        name="primary"
    )
    fallback = FakeSource(
        price=64000.0,
        healthy=True,
        name="fallback"
    )

    database, runtime, intelligence_flow, observer = build_runtime(
        tmp_path,
        primary,
        fallback
    )

    results = runtime.run(
        symbol="BTCUSDT",
        cycles=1
    )

    assert len(results) == 1

    observation = observer.observe("BTCUSDT")

    assert observation.price == 64000.0
    assert observation.source == "fallback"
    assert observation.fallback_used is True
    assert observation.source_status == "HEALTHY"

    result = results[0]
    market_context = result["market_context"]
    report = result["report"]

    assert market_context is not None
    assert report is not None

    assert len(intelligence_flow.consensus_history) == 1
    assert len(intelligence_flow.report_history) == 1

    consensus = intelligence_flow.consensus_history[0]

    assert consensus is not None
    assert report.trend == market_context.trend

    database.close()


def test_blind_market_data_blocks_intelligence(tmp_path):
    primary = FakeSource(
        price=65000.0,
        healthy=False,
        name="primary"
    )
    fallback = FakeSource(
        price=64000.0,
        healthy=False,
        name="fallback"
    )

    database, runtime, intelligence_flow, observer = build_runtime(
        tmp_path,
        primary,
        fallback
    )

    results = runtime.run(
        symbol="BTCUSDT",
        cycles=1
    )

    assert results == []
    assert intelligence_flow.consensus_history == []
    assert intelligence_flow.report_history == []

    observation = observer.observe("BTCUSDT")

    assert observation.price is None
    assert observation.source is None
    assert observation.source_status == "BLIND"

    database.close()
