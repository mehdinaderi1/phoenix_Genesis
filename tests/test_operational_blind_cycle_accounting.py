from core.database import DatabaseManager
from core.market_data.observer import RealMarketObserver
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime
from core.market_data.pipeline import MarketDataPipeline
from core.market_data.source_manager import MarketDataSourceManager
from exchanges.mock_exchange import MockExchange


class BlindSource:
    def health_check(self):
        return False

    def connect(self):
        raise RuntimeError("source unavailable")

    def get_price(self, symbol):
        raise RuntimeError("source unavailable")


def test_blind_cycles_are_accounted_for(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    exchange = MockExchange()
    pipeline = MarketDataPipeline(exchange, database)

    source_manager = MarketDataSourceManager({
        "blind": BlindSource(),
    })

    observer = RealMarketObserver(source_manager)

    runtime = OperationalMarketContextRuntime(
        observer=observer,
        market_data_pipeline=pipeline,
        database=database,
    )

    attempted_cycles = 3
    blind_results = []

    for _ in range(attempted_cycles):
        result = runtime.run_cycle("BTCUSDT")
        blind_results.append(result)

    assert len(blind_results) == attempted_cycles
    assert all(
        result["observation"].source_status == "BLIND"
        for result in blind_results
    )
    assert all(
        result["context"] is None
        for result in blind_results
    )

    database.close()
