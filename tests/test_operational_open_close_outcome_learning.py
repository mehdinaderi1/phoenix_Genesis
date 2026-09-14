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


class ChangingSourceManager:
    def __init__(self):
        self.prices = [65000.0, 66000.0]
        self.index = 0

    def get_price(self, symbol):
        price = self.prices[min(self.index, len(self.prices) - 1)]
        self.index += 1

        return MarketData(
            symbol=symbol,
            price=price,
            source="prototype",
            fallback_used=False,
            source_status="HEALTHY"
        )


class ChangingMarketExchange(MockExchange):
    def __init__(self):
        super().__init__()

        for timeframe in ("30m", "4H", "1D"):
            self.set_candle_sequence(
                "BTCUSDT",
                timeframe,
                [
                    {
                        "timestamp": 100,
                        "open": 66000.0,
                        "high": 66100.0,
                        "low": 65900.0,
                        "close": 66000.0,
                        "volume": 10.0
                    },
                    {
                        "timestamp": 101,
                        "open": 66000.0,
                        "high": 66100.0,
                        "low": 65900.0,
                        "close": 66000.0,
                        "volume": 11.0
                    }
                ]
            )


class ExecutableLearningFlow:
    def __init__(self):
        self.calls = 0

    def create_report(self, consensus):
        self.calls += 1

        if self.calls == 1:
            decision_action = "PREPARE_LONG"
            proposal_action = "PREPARE_LONG"
        else:
            decision_action = "PREPARE_SHORT"
            proposal_action = "PREPARE_SHORT"

        decision = SimpleNamespace(
            action=decision_action,
            symbol="BTCUSDT",
            strategy={
                "name": "prototype_long_short"
            }
        )

        proposal = SimpleNamespace(
            action=proposal_action,
            status="APPROVED",
            reason="Controlled executable learning test",
            confidence=85.0,
            symbol="BTCUSDT",
            strategy={
                "name": "prototype_long_short"
            },
            risk_status="ACCEPTED",
            metadata={}
        )

        return SimpleNamespace(
            signal=decision_action,
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


def test_operational_open_close_outcome_learning(tmp_path):
    database = DatabaseManager(
        str(tmp_path / "prototype.db")
    )

    database.connect()
    seed_market(database)

    exchange = ChangingMarketExchange()

    exchange_manager = ExchangeManager()
    exchange_manager.set_exchange(exchange)

    pipeline = MarketDataPipeline(
        exchange_manager,
        database
    )

    observer = RealMarketObserver(
        ChangingSourceManager()
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
        intelligence_flow=ExecutableLearningFlow(),
        paper_trading_runtime=paper_runtime
    )

    results = runtime.run(
        symbol="BTCUSDT",
        cycles=2
    )

    assert len(results) == 2

    first = results[0]
    second = results[1]

    assert first["decision"].action == "PREPARE_LONG"
    assert first["action_proposal"].action == "PREPARE_LONG"
    assert first["translated_action_proposal"].action == "BUY"
    assert first["paper_result"]["action"] == "OPEN"
    assert first["paper_result"]["position"].side == "BUY"
    assert first["paper_result"]["position"].entry_price == 65000.0

    assert second["decision"].action == "PREPARE_SHORT"
    assert second["action_proposal"].action == "PREPARE_SHORT"
    assert second["translated_action_proposal"].action == "SELL"
    assert second["paper_result"]["action"] == "CLOSE"
    assert second["paper_result"]["realized_pnl"] > 0.0

    learning_result = second["paper_result"]["learning_result"]

    assert learning_result is not None
    assert learning_result["result"] == "SUCCESS"
    assert learning_result["score"] == 100
    assert learning_result["performance"] is not None
    assert learning_result["performance"].success is True
    assert learning_result["performance"].profit_loss == 1000.0
    assert learning_result["performance_learning"] is not None

    assert session.get_position() is None
    assert session.get_trade_count() == 1
    assert session.get_total_pnl() > 0.0
    assert session.get_balance() > 1000.0

    print("OPEN -> CLOSE -> LEARNING")
    print("  entry=65000.0")
    print("  exit=66000.0")
    print(
        "  action_1={}".format(
            first["paper_result"]["action"]
        )
    )
    print(
        "  action_2={}".format(
            second["paper_result"]["action"]
        )
    )
    print(
        "  realized_pnl={}".format(
            second["paper_result"]["realized_pnl"]
        )
    )
    print(
        "  learning_result={}".format(
            learning_result["result"]
        )
    )
    print(
        "  learning_score={}".format(
            learning_result["score"]
        )
    )
    print(
        "  performance_success={}".format(
            learning_result["performance"].success
        )
    )

    database.close()
