from core.database import DatabaseManager
from core.market_data.market_data import MarketData
from core.market_data.observer import RealMarketObserver
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime
from core.market_data.pipeline import MarketDataPipeline
from core.market_data.source_manager import MarketDataSourceManager
from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from exchanges.exchange_manager import ExchangeManager
from exchanges.mock_exchange import MockExchange
from intelligence.flow import IntelligenceFlow
from execution.paper_trading_session import PaperTradingSession
from execution.paper_session_archive import PaperSessionArchive
from execution.paper_trading_runtime import PaperTradingRuntime


class FakeSourceManager:
    def get_price(self, symbol):
        return MarketData(
            symbol=symbol,
            price=65000.0,
            source="mock",
            fallback_used=False,
            source_status="HEALTHY"
        )


def test_operational_prototype_composition(tmp_path):
    database = DatabaseManager(str(tmp_path / "prototype.db"))
    database.connect()

    exchange = MockExchange()

    for timeframe in ("30m", "4H", "1D"):
        exchange.set_candle_sequence(
            "BTCUSDT",
            timeframe,
            [{
                "timestamp": 1001,
                "open": 65000,
                "high": 65100,
                "low": 64900,
                "close": 65000,
                "volume": 1
            }]
        )

    exchange_manager = ExchangeManager()
    exchange_manager.set_exchange(exchange)

    market_data_pipeline = MarketDataPipeline(
        exchange_manager,
        database
    )

    observer = RealMarketObserver(FakeSourceManager())

    market_context_runtime = OperationalMarketContextRuntime(
        observer=observer,
        market_data_pipeline=market_data_pipeline,
        database=database
    )

    intelligence_flow = IntelligenceFlow()
    intelligence_flow.enable_inline_outcome_learning = False

    session = PaperTradingSession(
        initial_balance=1000,
        position_size_percent=10
    )

    archive = PaperSessionArchive(
        root_path=str(tmp_path / "sessions")
    )

    paper_runtime = PaperTradingRuntime(session=session)

    runtime = OperationalPaperRuntime(
        market_context_runtime=market_context_runtime,
        intelligence_flow=intelligence_flow,
        paper_trading_runtime=paper_runtime,
        session_archive=archive
    )

    results = runtime.run(
        symbol="BTCUSDT",
        cycles=3
    )

    assert len(results) == 3

    for result in results:
        assert result["observation"] is not None
        assert result["market_context"] is not None
        assert result["intelligence_context"] is not None
        assert result["report"] is not None
        assert result["decision"] is not None
        assert result["action_proposal"] is not None
        assert result["translated_action_proposal"] is not None
        assert result["paper_result"] is not None
        assert result["error"] is None

    assert results[0]["observation"].price == 65000.0
    assert results[1]["observation"].price == 65000.0
    assert results[2]["observation"].price == 65000.0

    assert session.session_id
    assert session.get_balance() >= 0
    assert session.get_trade_count() >= 0

    database.close()
