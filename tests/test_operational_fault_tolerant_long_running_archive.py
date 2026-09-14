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


class FaultTolerantSource:
    def __init__(self):
        self.prices = [
            65000.0,
            65500.0,
            66000.0,
            66000.0,
            65500.0,
            65000.0,
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


class FaultTolerantMarketRuntime:
    def __init__(self, runtime):
        self.runtime = runtime
        self.calls = 0

    def run_cycle(self, symbol="BTCUSDT"):
        self.calls += 1

        if self.calls == 3:
            raise RuntimeError(
                "Injected operational cycle failure"
            )

        return self.runtime.run_cycle(symbol=symbol)


class FaultTolerantExchange(MockExchange):
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
                "open": 65500.0,
                "high": 65600.0,
                "low": 65400.0,
                "close": 65500.0,
                "volume": 11.0,
            },
            {
                "timestamp": 102,
                "open": 66000.0,
                "high": 66100.0,
                "low": 65900.0,
                "close": 66000.0,
                "volume": 12.0,
            },
            {
                "timestamp": 103,
                "open": 66000.0,
                "high": 66100.0,
                "low": 65900.0,
                "close": 66000.0,
                "volume": 13.0,
            },
            {
                "timestamp": 104,
                "open": 65500.0,
                "high": 65600.0,
                "low": 65400.0,
                "close": 65500.0,
                "volume": 14.0,
            },
            {
                "timestamp": 105,
                "open": 65000.0,
                "high": 65100.0,
                "low": 64900.0,
                "close": 65000.0,
                "volume": 15.0,
            },
        ]

        for timeframe in ("30m", "4H", "1D"):
            self.set_candle_sequence(
                "BTCUSDT",
                timeframe,
                candles,
            )


class FaultTolerantLearningFlow:
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
            "PREPARE_LONG",
        ]

        action = actions[
            min(self.calls - 1, len(actions) - 1)
        ]

        decision = SimpleNamespace(
            action=action,
            symbol="BTCUSDT",
            strategy={
                "name": "fault_tolerant_prototype",
            },
        )

        proposal = SimpleNamespace(
            action=action,
            status="APPROVED",
            reason="Controlled fault-tolerant archive test",
            confidence=85.0,
            symbol="BTCUSDT",
            strategy={
                "name": "fault_tolerant_prototype",
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


def test_fault_tolerant_long_running_session_archive(tmp_path):
    database = DatabaseManager(
        str(tmp_path / "prototype.db")
    )

    database.connect()
    seed_market(database)

    exchange = FaultTolerantExchange()

    exchange_manager = ExchangeManager()
    exchange_manager.set_exchange(exchange)

    pipeline = MarketDataPipeline(
        exchange_manager,
        database,
    )

    observer = RealMarketObserver(
        FaultTolerantSource()
    )

    base_market_runtime = OperationalMarketContextRuntime(
        observer=observer,
        market_data_pipeline=pipeline,
        database=database,
    )

    market_runtime = FaultTolerantMarketRuntime(
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
        intelligence_flow=FaultTolerantLearningFlow(),
        paper_trading_runtime=paper_runtime,
        session_archive=archive,
    )

    results = runtime.run(
        symbol="BTCUSDT",
        cycles=6,
        continue_on_error=True,
    )

    assert len(results) == 6

    assert results[0]["paper_result"]["action"] == "OPEN"
    assert results[1]["paper_result"]["action"] == "HOLD"

    assert results[2]["error"] is not None
    assert "Injected operational cycle failure" in str(
        results[2]["error"]
    )
    assert results[2]["paper_result"] is None

    assert results[3]["paper_result"]["action"] == "CLOSE"
    assert results[4]["paper_result"]["action"] == "OPEN"
    assert results[5]["paper_result"]["action"] == "HOLD"

    learning_results = [
        result["paper_result"]["learning_result"]
        for result in results
        if result["paper_result"] is not None
        and result["paper_result"]["learning_result"] is not None
    ]

    assert len(learning_results) == 1
    assert learning_results[0]["result"] == "SUCCESS"

    assert session.get_trade_count() == 1
    assert session.get_position() is not None
    assert session.get_position().side == "SELL"

    session_id = session.session_id

    archived = archive.load(session_id)

    assert archived is not None
    assert archived["session_id"] == session_id
    assert len(archived["cycles"]) == 6

    assert archived["cycles"][2]["error"] == (
        "Injected operational cycle failure"
    )

    assert archived["cycles"][2]["action"] is None

    assert archived["summary"]["cycles_processed"] == 6
    assert archived["summary"]["open_count"] == 2
    assert archived["summary"]["hold_count"] == 2
    assert archived["summary"]["close_count"] == 1
    assert archived["summary"]["trade_count"] == 1
    assert archived["final_position"] is not None

    print("FAULT-TOLERANT LONG-RUNNING ARCHIVE")
    print("  cycles={}".format(len(archived["cycles"])))
    print("  failed_cycle=3")
    print("  open={}".format(archived["summary"]["open_count"]))
    print("  hold={}".format(archived["summary"]["hold_count"]))
    print("  close={}".format(archived["summary"]["close_count"]))
    print("  learning_events={}".format(len(learning_results)))
    print("  trades={}".format(archived["summary"]["trade_count"]))
    print("  final_position={}".format(
        archived["final_position"]
    ))
    print("  archive_load=SUCCESS")

    database.close()
