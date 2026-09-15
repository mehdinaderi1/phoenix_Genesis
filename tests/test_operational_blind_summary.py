from core.database import DatabaseManager
from core.market_data.observer import RealMarketObserver
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime
from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from core.market_data.pipeline import MarketDataPipeline
from core.market_data.source_manager import MarketDataSourceManager
from exchanges.mock_exchange import MockExchange
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession
from intelligence.flow import IntelligenceFlow


class BlindSource:
    def health_check(self):
        return False

    def connect(self):
        raise RuntimeError("source unavailable")

    def get_price(self, symbol):
        raise RuntimeError("source unavailable")


def test_build_summary_counts_blind_cycles(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    exchange = MockExchange()
    pipeline = MarketDataPipeline(exchange, database)

    source_manager = MarketDataSourceManager({
        "blind": BlindSource(),
    })

    observer = RealMarketObserver(source_manager)

    market_runtime = OperationalMarketContextRuntime(
        observer=observer,
        market_data_pipeline=pipeline,
        database=database,
    )

    intelligence_flow = IntelligenceFlow()
    paper_session = PaperTradingSession()
    paper_runtime = PaperTradingRuntime(
        session=paper_session
    )

    operational_runtime = OperationalPaperRuntime(
        market_context_runtime=market_runtime,
        intelligence_flow=intelligence_flow,
        paper_trading_runtime=paper_runtime
    )

    results = operational_runtime.run(
        symbol="BTCUSDT",
        cycles=3
    )

    summary = operational_runtime.build_summary(results)

    assert len(results) == 3
    assert summary["cycles_processed"] == 3
    assert summary["successful_cycles"] == 0
    assert summary["blind_cycles"] == 3
    assert summary["error_cycles"] == 0
    assert summary["open_count"] == 0
    assert summary["hold_count"] == 0
    assert summary["close_count"] == 0
    assert summary["trade_count"] == 0

    database.close()
