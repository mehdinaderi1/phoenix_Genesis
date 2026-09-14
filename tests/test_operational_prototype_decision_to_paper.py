from types import SimpleNamespace

from core.database import DatabaseManager
from core.market_data.market_data import MarketData
from core.market_data.observer import RealMarketObserver
from core.market_data.operational_market_context import OperationalMarketContext
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime
from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from core.market_data.pipeline import MarketDataPipeline
from execution.paper_session_archive import PaperSessionArchive
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession
from exchanges.exchange_manager import ExchangeManager
from exchanges.mock_exchange import MockExchange
from intelligence.flow import IntelligenceFlow


class FakeSourceManager:
    def __init__(self):
        self.calls = 0

    def get_price(self, symbol):
        prices = [65000.0, 65500.0, 66000.0]
        price = prices[self.calls]
        self.calls += 1
        return MarketData(
            symbol=symbol,
            price=price,
            source="mock",
            fallback_used=False,
            source_status="HEALTHY"
        )


class ControlledOperationalIntelligenceFlow:
    def __init__(self):
        self.real_flow = IntelligenceFlow()
        self.real_flow.enable_inline_outcome_learning = False
        self.calls = 0
        self.decision_outcome_bridge = self.real_flow.decision_outcome_bridge

    def create_report(self, consensus):
        report = self.real_flow.create_report(consensus)

        actions = ("PREPARE_LONG", "WAIT", "PREPARE_SHORT")
        action = actions[self.calls]
        self.calls += 1

        strategy = {
            "name": "OPERATIONAL_PAPER_TEST_STRATEGY"
        }

        report.decision.action = action
        report.decision.strategy = strategy

        report.action_proposal = SimpleNamespace(
            action=action,
            status="APPROVED",
            reason=f"Controlled operational action: {action}",
            confidence=85.0,
            symbol="BTCUSDT",
            strategy=strategy,
            risk_status="LOW",
            metadata={}
        )

        return report


def test_operational_prototype_decision_to_paper_reaction(tmp_path):
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

    intelligence = ControlledOperationalIntelligenceFlow()

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0,
        outcome_bridge=intelligence.decision_outcome_bridge
    )

    archive = PaperSessionArchive(
        root_path=str(tmp_path / "sessions")
    )

    paper_runtime = PaperTradingRuntime(session)

    runtime = OperationalPaperRuntime(
        market_context_runtime,
        intelligence,
        paper_runtime,
        session_archive=archive
    )

    results = runtime.run(
        symbol="BTCUSDT",
        cycles=3
    )

    assert len(results) == 3
    assert intelligence.calls == 3

    assert results[0]["translated_action_proposal"].action == "BUY"
    assert results[1]["translated_action_proposal"].action == "WAIT"
    assert results[2]["translated_action_proposal"].action == "SELL"

    assert results[0]["paper_result"]["action"] == "OPEN"
    assert results[1]["paper_result"]["action"] == "HOLD"
    assert results[2]["paper_result"]["action"] == "CLOSE"

    learning_result = results[2]["paper_result"]["learning_result"]

    assert learning_result is not None
    assert learning_result["performance_learning"] is not None
    assert learning_result["performance_learning"]["outcome"] == "SUCCESS"
    assert learning_result["performance_learning"]["experience"] is not None

    experiences = intelligence.real_flow.experience_memory.experiences

    assert len(experiences) == 1

    experience = experiences[0]
    assert experience.success is True
    assert experience.score == 100
    assert experience.strategy == "OPERATIONAL_PAPER_TEST_STRATEGY"

    assert session.get_position() is None
    assert session.get_trade_count() == 1
    assert session.get_total_pnl() > 0

    summary = runtime.build_summary(results)

    assert summary["cycles_processed"] == 3
    assert summary["open_count"] == 1
    assert summary["hold_count"] == 1
    assert summary["close_count"] == 1
    assert summary["current_position"] is None
    assert summary["trade_count"] == 1
    assert summary["total_pnl"] > 0

    database.close()
