from types import SimpleNamespace

from core.engine import PhoenixEngine
from exchanges.exchange_manager import ExchangeManager
from exchanges.mock_exchange import MockExchange
from core.market_data.pipeline import MarketDataPipeline
from analysis.multi_timeframe_pipeline import MultiTimeframePipeline
from intelligence.flow import IntelligenceFlow
from execution.paper_trading_session import PaperTradingSession
from execution.paper_market_cycle_runner import PaperMarketCycleRunner


class ControlledActionIntelligenceFlow:

    def __init__(self):
        self.real_flow = IntelligenceFlow()
        self.real_flow.enable_inline_outcome_learning = False
        self.calls = 0
        self.decisions = []

        self.decision_outcome_bridge = (
            self.real_flow.decision_outcome_bridge
        )

    def create_report(self, consensus):
        report = self.real_flow.create_report(consensus)

        self.decisions.append(report.decision)

        report.decision.action = "PREPARE_LONG"
        report.decision.strategy = {
            "name": "PAPER_TEST_STRATEGY"
        }

        actions = ("BUY", "WAIT", "SELL")
        action = actions[self.calls]
        self.calls += 1

        report.action_proposal = SimpleNamespace(
            action=action,
            status="APPROVED",
            reason=f"Controlled PAPER action: {action}",
            symbol="BTCUSDT"
        )

        return report


def test_paper_runner_real_intelligence_triggers_real_outcome_learning():

    engine = PhoenixEngine()
    engine.start()

    exchange_manager = ExchangeManager()
    mock = MockExchange()

    mock.set_price_sequence(
        "BTCUSDT",
        [65000.0, 65500.0, 66000.0]
    )

    exchange_manager.set_exchange(mock)
    assert exchange_manager.connect()

    market_data_pipeline = MarketDataPipeline(
        exchange_manager,
        engine.database
    )

    multi_timeframe_pipeline = MultiTimeframePipeline(
        engine.database
    )

    for timeframe in ("30m", "4H", "1D"):
        market_data_pipeline.fetch_and_store_historical(
            symbol="BTCUSDT",
            timeframe=timeframe,
            limit=30
        )

    intelligence_flow = ControlledActionIntelligenceFlow()

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0
    )

    runner = PaperMarketCycleRunner(
        exchange_manager=exchange_manager,
        multi_timeframe_pipeline=multi_timeframe_pipeline,
        intelligence_flow=intelligence_flow,
        session=session,
        market_data_pipeline=market_data_pipeline
    )

    results = runner.run(
        cycle_count=3,
        symbol="BTCUSDT"
    )

    assert len(results) == 3

    assert results[0]["action"] == "OPEN"
    assert results[1]["action"] == "HOLD"
    assert results[2]["action"] == "CLOSE"

    assert results[2]["realized_pnl"] > 0
    assert results[2]["learning_result"] is not None

    learning_result = results[2]["learning_result"]
    performance_learning = learning_result["performance_learning"]

    assert performance_learning["outcome"] == "SUCCESS"
    assert performance_learning["experience"] is not None

    experiences = (
        intelligence_flow.real_flow.experience_memory.experiences
    )

    assert len(experiences) == 1

    experience = experiences[0]

    assert experience.success is True
    assert experience.score == 100
    assert experience.strategy == "PAPER_TEST_STRATEGY"

    summary = runner.paper_runtime.build_summary(results)

    assert summary["cycles_processed"] == 3
    assert summary["open_count"] == 1
    assert summary["hold_count"] == 1
    assert summary["close_count"] == 1
    assert summary["current_position"] is None
    assert summary["total_pnl"] > 0
    assert summary["trade_count"] == 1
