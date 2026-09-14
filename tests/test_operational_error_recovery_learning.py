from types import SimpleNamespace

from core.database import DatabaseManager
from core.market_data.market_data import MarketData
from core.market_data.observer import RealMarketObserver
from core.market_data.operational_market_context_runtime import (
    OperationalMarketContextRuntime,
)
from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from core.market_data.pipeline import MarketDataPipeline
from exchanges.exchange_manager import ExchangeManager
from exchanges.mock_exchange import MockExchange
from execution.paper_session_archive import PaperSessionArchive
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession
from intelligence.decision_outcome_bridge import DecisionOutcomeBridge
from intelligence.memory.experience_memory import ExperienceMemory
from intelligence.memory.outcome_memory import OutcomeMemory
from intelligence.memory.strategy_performance_memory import (
    StrategyPerformanceMemory,
)
from intelligence.performance_feedback import PerformanceFeedback
from intelligence.performance_learning_adapter import (
    PerformanceLearningAdapter,
)


class RecoverySource:
    def __init__(self):
        self.prices = [
            65000.0,
            66000.0,
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
            source_status="HEALTHY",
        )


class RecoveryExchange(MockExchange):
    def __init__(self):
        super().__init__()

        candles = [
            {
                "timestamp": 100,
                "open": 65000.0,
                "high": 65100.0,
                "low": 64900.0,
                "close": 65000.0,
                "volume": 10.0,
            },
            {
                "timestamp": 101,
                "open": 66000.0,
                "high": 66100.0,
                "low": 65900.0,
                "close": 66000.0,
                "volume": 11.0,
            },
        ]

        for timeframe in ("30m", "4H", "1D"):
            self.set_candle_sequence(
                "BTCUSDT",
                timeframe,
                candles,
            )


class RecoveryMarketRuntime:
    def __init__(self, runtime):
        self.runtime = runtime
        self.calls = 0

    def run_cycle(self, symbol="BTCUSDT"):
        self.calls += 1

        if self.calls == 2:
            raise RuntimeError(
                "Injected recovery failure"
            )

        return self.runtime.run_cycle(
            symbol=symbol
        )


class RecoveryLearningFlow:
    def __init__(self):
        self.calls = 0

    def create_report(self, consensus):
        self.calls += 1

        actions = [
            "PREPARE_LONG",
            "PREPARE_SHORT",
        ]

        action = actions[
            min(self.calls - 1, len(actions) - 1)
        ]

        decision = SimpleNamespace(
            action=action,
            symbol="BTCUSDT",
            strategy={
                "name": "recovery_prototype",
            },
        )

        proposal = SimpleNamespace(
            action=action,
            status="APPROVED",
            reason="Controlled recovery test",
            confidence=85.0,
            symbol="BTCUSDT",
            strategy={
                "name": "recovery_prototype",
            },
            risk_status="ACCEPTED",
            metadata={},
        )

        return SimpleNamespace(
            signal=action,
            trend="BULLISH",
            confidence=85.0,
            regime="TRENDING",
            risk="ACCEPTED",
            decision=decision,
            action_proposal=proposal,
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
                    10.0,
                ),
            )

    database.connection.commit()


def test_operational_error_recovery_preserves_position_and_learning(
    tmp_path
):
    database = DatabaseManager(
        str(tmp_path / "prototype.db")
    )

    database.connect()
    seed_market(database)

    exchange = RecoveryExchange()

    exchange_manager = ExchangeManager()
    exchange_manager.set_exchange(exchange)

    pipeline = MarketDataPipeline(
        exchange_manager,
        database,
    )

    observer = RealMarketObserver(
        RecoverySource()
    )

    base_market_runtime = OperationalMarketContextRuntime(
        observer=observer,
        market_data_pipeline=pipeline,
        database=database,
    )

    market_runtime = RecoveryMarketRuntime(
        base_market_runtime
    )

    experience_memory = ExperienceMemory()

    performance_learning = PerformanceLearningAdapter(
        experience_memory
    )

    outcome_bridge = DecisionOutcomeBridge(
        outcome_memory=OutcomeMemory(),
        performance_feedback=PerformanceFeedback(),
        strategy_performance_memory=StrategyPerformanceMemory(),
        performance_learning=performance_learning,
    )

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0,
        outcome_bridge=outcome_bridge,
    )

    paper_runtime = PaperTradingRuntime(session)

    archive = PaperSessionArchive(
        root_path=str(tmp_path / "paper_sessions")
    )

    runtime = OperationalPaperRuntime(
        market_context_runtime=market_runtime,
        intelligence_flow=RecoveryLearningFlow(),
        paper_trading_runtime=paper_runtime,
        session_archive=archive,
    )

    results = runtime.run(
        symbol="BTCUSDT",
        cycles=3,
        continue_on_error=True,
    )

    assert len(results) == 3

    assert results[0]["paper_result"]["action"] == "OPEN"

    opened_position = results[0]["paper_result"]["position"]

    assert opened_position is not None
    assert opened_position.side == "BUY"
    assert opened_position.entry_price == 65000.0

    assert results[1]["error"] is not None
    assert "Injected recovery failure" in str(
        results[1]["error"]
    )
    assert results[1]["paper_result"] is None

    assert results[2]["paper_result"]["action"] == "CLOSE"

    learning_result = (
        results[2]["paper_result"]["learning_result"]
    )

    assert learning_result is not None
    assert learning_result["result"] == "SUCCESS"
    assert learning_result["score"] == 100

    assert session.get_position() is None
    assert session.get_trade_count() == 1
    assert session.get_total_pnl() > 0.0

    archived = archive.load(
        session.session_id
    )

    assert archived is not None
    assert len(archived["cycles"]) == 3

    assert archived["cycles"][0]["action"] == "OPEN"

    assert archived["cycles"][1]["error"] == (
        "Injected recovery failure"
    )

    assert archived["cycles"][1]["action"] is None
    assert archived["cycles"][2]["action"] == "CLOSE"

    assert archived["summary"]["cycles_processed"] == 3
    assert archived["summary"]["open_count"] == 1
    assert archived["summary"]["hold_count"] == 0
    assert archived["summary"]["close_count"] == 1
    assert archived["summary"]["trade_count"] == 1
    assert archived["summary"]["total_pnl"] > 0.0
    assert archived["final_position"] is None

    print("OPERATIONAL ERROR RECOVERY")
    print("  cycles=3")
    print("  cycle_1=OPEN")
    print("  cycle_2=ERROR")
    print("  cycle_3=CLOSE")
    print("  learning=SUCCESS")
    print(
        "  trades={}".format(
            session.get_trade_count()
        )
    )
    print(
        "  total_pnl={}".format(
            session.get_total_pnl()
        )
    )
    print(
        "  final_position={}".format(
            session.get_position()
        )
    )
    print("  archive_load=SUCCESS")

    database.close()
