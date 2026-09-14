from types import SimpleNamespace

from core.database import DatabaseManager
from core.market_data.market_data import MarketData
from core.market_data.observer import RealMarketObserver
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime
from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from core.market_data.pipeline import MarketDataPipeline
from exchanges.exchange_manager import ExchangeManager
from exchanges.mock_exchange import MockExchange
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession
from intelligence.decision_outcome_bridge import DecisionOutcomeBridge
from intelligence.memory.experience_memory import ExperienceMemory
from intelligence.memory.outcome_memory import OutcomeMemory
from intelligence.memory.strategy_performance_memory import StrategyPerformanceMemory
from intelligence.performance_feedback import PerformanceFeedback
from intelligence.performance_learning_adapter import PerformanceLearningAdapter


class LongRunningSourceManager:
    def __init__(self):
        self.prices = [
            65000.0,
            65500.0,
            66000.0,
            66000.0,
            65500.0,
            65000.0
        ]
        self.index = 0

    def get_price(self, symbol):
        price = self.prices[
            min(self.index, len(self.prices) - 1)
        ]
        self.index += 1

        return MarketData(
            symbol=symbol,
            price=price,
            source="prototype",
            fallback_used=False,
            source_status="HEALTHY"
        )


class LongRunningMarketExchange(MockExchange):
    def __init__(self):
        super().__init__()

        candles = [
            {
                "timestamp": 100,
                "open": 65000.0,
                "high": 65100.0,
                "low": 64900.0,
                "close": 65000.0,
                "volume": 10.0
            },
            {
                "timestamp": 101,
                "open": 65500.0,
                "high": 65600.0,
                "low": 65400.0,
                "close": 65500.0,
                "volume": 11.0
            },
            {
                "timestamp": 102,
                "open": 66000.0,
                "high": 66100.0,
                "low": 65900.0,
                "close": 66000.0,
                "volume": 12.0
            },
            {
                "timestamp": 103,
                "open": 66000.0,
                "high": 66100.0,
                "low": 65900.0,
                "close": 66000.0,
                "volume": 13.0
            },
            {
                "timestamp": 104,
                "open": 65500.0,
                "high": 65600.0,
                "low": 65400.0,
                "close": 65500.0,
                "volume": 14.0
            },
            {
                "timestamp": 105,
                "open": 65000.0,
                "high": 65100.0,
                "low": 64900.0,
                "close": 65000.0,
                "volume": 15.0
            }
        ]

        for timeframe in ("30m", "4H", "1D"):
            self.set_candle_sequence(
                "BTCUSDT",
                timeframe,
                candles
            )


class LongRunningLearningFlow:
    def __init__(self):
        self.calls = 0

    def create_report(self, consensus):
        self.calls += 1

        actions = [
            "PREPARE_LONG",
            "WAIT",
            "PREPARE_SHORT",
            "PREPARE_SHORT",
            "WAIT",
            "PREPARE_LONG"
        ]

        action = actions[
            min(self.calls - 1, len(actions) - 1)
        ]

        decision = SimpleNamespace(
            action=action,
            symbol="BTCUSDT",
            strategy={
                "name": "long_running_prototype"
            }
        )

        proposal = SimpleNamespace(
            action=action,
            status="APPROVED",
            reason="Controlled long-running learning test",
            confidence=85.0,
            symbol="BTCUSDT",
            strategy={
                "name": "long_running_prototype"
            },
            risk_status="ACCEPTED",
            metadata={}
        )

        return SimpleNamespace(
            signal=action,
            trend="BULLISH",
            confidence=85.0,
            regime="TRENDING",
            risk="ACCEPTED",
            decision=decision,
            action_proposal=proposal
        )


def seed_market(database):
    for timeframe in ("30m", "4H", "1D"):
        for index in range(5):
            price = 65000.0

            database.connection.execute(
                "INSERT INTO market_candles "
                "(symbol, timeframe, timestamp, open, high, low, close, volume) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    "BTCUSDT",
                    timeframe,
                    index + 1,
                    price,
                    price + 100.0,
                    price - 100.0,
                    price,
                    10.0
                )
            )

    database.connection.commit()


def test_operational_long_running_learning(tmp_path):
    database = DatabaseManager(
        str(tmp_path / "prototype.db")
    )

    database.connect()
    seed_market(database)

    exchange = LongRunningMarketExchange()

    exchange_manager = ExchangeManager()
    exchange_manager.set_exchange(exchange)

    pipeline = MarketDataPipeline(
        exchange_manager,
        database
    )

    observer = RealMarketObserver(
        LongRunningSourceManager()
    )

    market_runtime = OperationalMarketContextRuntime(
        observer=observer,
        market_data_pipeline=pipeline,
        database=database
    )

    experience_memory = ExperienceMemory()

    performance_learning = PerformanceLearningAdapter(
        experience_memory
    )

    outcome_bridge = DecisionOutcomeBridge(
        outcome_memory=OutcomeMemory(),
        performance_feedback=PerformanceFeedback(),
        strategy_performance_memory=StrategyPerformanceMemory(),
        performance_learning=performance_learning
    )

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0,
        outcome_bridge=outcome_bridge
    )

    paper_runtime = PaperTradingRuntime(session)

    runtime = OperationalPaperRuntime(
        market_context_runtime=market_runtime,
        intelligence_flow=LongRunningLearningFlow(),
        paper_trading_runtime=paper_runtime
    )

    results = runtime.run(
        symbol="BTCUSDT",
        cycles=6
    )

    assert len(results) == 6

    expected_decisions = [
        "PREPARE_LONG",
        "WAIT",
        "PREPARE_SHORT",
        "PREPARE_SHORT",
        "WAIT",
        "PREPARE_LONG"
    ]

    expected_actions = [
        "OPEN",
        "HOLD",
        "CLOSE",
        "OPEN",
        "HOLD",
        "CLOSE"
    ]

    for index, result in enumerate(results):
        assert result["decision"].action == expected_decisions[index]
        assert result["action_proposal"].action == expected_decisions[index]

    paper_actions = [
        result["paper_result"]["action"]
        for result in results
    ]

    assert paper_actions == expected_actions

    assert results[0]["translated_action_proposal"].action == "BUY"
    assert results[2]["translated_action_proposal"].action == "SELL"
    assert results[3]["translated_action_proposal"].action == "SELL"
    assert results[5]["translated_action_proposal"].action == "BUY"

    assert results[0]["paper_result"]["position"].side == "BUY"
    assert results[0]["paper_result"]["position"].entry_price == 65000.0

    assert results[2]["paper_result"]["realized_pnl"] > 0.0
    assert results[2]["paper_result"]["learning_result"] is not None
    assert results[2]["paper_result"]["learning_result"]["result"] == "SUCCESS"
    assert results[2]["paper_result"]["learning_result"]["score"] == 100

    assert results[3]["paper_result"]["position"].side == "SELL"
    assert results[3]["paper_result"]["position"].entry_price == 66000.0

    assert results[5]["paper_result"]["realized_pnl"] > 0.0
    assert results[5]["paper_result"]["learning_result"] is not None
    assert results[5]["paper_result"]["learning_result"]["result"] == "SUCCESS"
    assert results[5]["paper_result"]["learning_result"]["score"] == 100

    learning_results = [
        result["paper_result"]["learning_result"]
        for result in results
        if result["paper_result"]["learning_result"] is not None
    ]

    assert len(learning_results) == 2

    assert session.get_position() is None
    assert session.get_trade_count() == 2
    assert session.get_total_pnl() > 0.0
    assert session.get_balance() > 1000.0

    print("LONG-RUNNING OPERATIONAL LEARNING")
    print("  cycles=6")
    print("  actions={}".format(paper_actions))
    print("  learning_events={}".format(len(learning_results)))
    print("  trades={}".format(session.get_trade_count()))
    print("  total_pnl={}".format(session.get_total_pnl()))
    print("  final_position={}".format(session.get_position()))

    database.close()
