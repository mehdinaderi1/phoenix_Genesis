import json
from types import SimpleNamespace

from execution.paper_market_cycle_runner import (
    PaperMarketCycleRunner
)
from execution.paper_trading_session import (
    PaperTradingSession
)


class FakeExchangeManager:

    def __init__(self):
        self.calls = 0

    def get_price(self, symbol):
        self.calls += 1
        return 65000.0


class FakeMultiTimeframePipeline:

    def __init__(self):
        self.calls = 0

    def analyze(self, symbol):
        self.calls += 1
        return SimpleNamespace(
            signal="BUY"
        )


class FakeIntelligenceFlow:

    def __init__(self):
        self.calls = 0

    def create_report(self, consensus):
        self.calls += 1

        proposal = SimpleNamespace(
            action="WAIT",
            status="REJECTED",
            reason="Monitoring",
            symbol="BTCUSDT"
        )

        return SimpleNamespace(
            symbol="BTCUSDT",
            timeframe="30m",
            trend="BULLISH",
            regime="RANGING",
            signal="BUY",
            confidence=70,
            risk="MEDIUM",
            reasons=["Monitoring"],
            action_proposal=proposal
        )


def test_paper_market_cycle_runner_builds_bounded_cycles():

    exchange_manager = FakeExchangeManager()

    pipeline = FakeMultiTimeframePipeline()

    intelligence_flow = FakeIntelligenceFlow()

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    runner = PaperMarketCycleRunner(
        exchange_manager=exchange_manager,
        multi_timeframe_pipeline=pipeline,
        intelligence_flow=intelligence_flow,
        session=session
    )

    results = runner.run(
        cycle_count=3,
        symbol="BTCUSDT"
    )

    assert len(results) == 3

    assert exchange_manager.calls == 3
    assert pipeline.calls == 3
    assert intelligence_flow.calls == 3

    assert all(
        result["action"] == "HOLD"
        for result in results
    )

    assert session.get_position() is None
    assert session.get_trade_count() == 0
    assert session.get_balance() == 1000.0


def test_paper_market_cycle_runner_builds_summary():

    exchange_manager = FakeExchangeManager()
    pipeline = FakeMultiTimeframePipeline()
    intelligence_flow = FakeIntelligenceFlow()

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    runner = PaperMarketCycleRunner(
        exchange_manager=exchange_manager,
        multi_timeframe_pipeline=pipeline,
        intelligence_flow=intelligence_flow,
        session=session
    )

    results = runner.run(
        cycle_count=3,
        symbol="BTCUSDT"
    )

    summary = runner.build_summary(
        results
    )

    assert summary["cycles_processed"] == 3
    assert summary["open_count"] == 0
    assert summary["hold_count"] == 3
    assert summary["close_count"] == 0

    assert summary["current_position"] is None
    assert summary["balance"] == 1000.0
    assert summary["total_pnl"] == 0.0
    assert summary["trade_count"] == 0


def test_paper_market_cycle_runner_builds_cycle_records():

    exchange_manager = FakeExchangeManager()
    pipeline = FakeMultiTimeframePipeline()
    intelligence_flow = FakeIntelligenceFlow()

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    runner = PaperMarketCycleRunner(
        exchange_manager=exchange_manager,
        multi_timeframe_pipeline=pipeline,
        intelligence_flow=intelligence_flow,
        session=session
    )

    results = runner.run(
        cycle_count=3,
        symbol="BTCUSDT"
    )

    records = runner.build_cycle_records(
        results
    )

    assert len(records) == 3

    assert records[0]["cycle"] == 1
    assert records[0]["symbol"] == "BTCUSDT"
    assert records[0]["price"] == 65000.0
    assert records[0]["signal"] == "BUY"

    assert records[0]["trend"] == "BULLISH"
    assert records[0]["regime"] == "RANGING"
    assert records[0]["confidence"] == 70
    assert records[0]["risk"] == "MEDIUM"

    assert records[0]["proposal_action"] == "WAIT"
    assert records[0]["proposal_status"] == "REJECTED"
    assert records[0]["proposal_reason"] == "Monitoring"

    assert records[0]["action"] == "HOLD"
    assert records[0]["execution_status"] is None
    assert records[0]["realized_pnl"] == 0.0

    assert records[0]["position_side"] is None
    assert records[0]["entry_price"] is None
    assert records[0]["quantity"] is None

    assert records[0]["position"] is None
    assert records[0]["report"] is not None

    assert records[1]["cycle"] == 2
    assert records[2]["cycle"] == 3

    assert all(
        record["action"] == "HOLD"
        for record in records
    )

def test_paper_market_cycle_runner_builds_json_serializable_cycle_records():

    exchange_manager = FakeExchangeManager()
    pipeline = FakeMultiTimeframePipeline()
    intelligence_flow = FakeIntelligenceFlow()

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    runner = PaperMarketCycleRunner(
        exchange_manager=exchange_manager,
        multi_timeframe_pipeline=pipeline,
        intelligence_flow=intelligence_flow,
        session=session
    )

    results = runner.run(
        cycle_count=3,
        symbol="BTCUSDT"
    )

    records = (
        runner.build_serializable_cycle_records(
            results
        )
    )

    assert len(records) == 3

    assert records[0]["cycle"] == 1
    assert records[0]["symbol"] == "BTCUSDT"
    assert records[0]["price"] == 65000.0
    assert records[0]["signal"] == "BUY"

    assert records[0]["trend"] == "BULLISH"
    assert records[0]["regime"] == "RANGING"
    assert records[0]["confidence"] == 70
    assert records[0]["risk"] == "MEDIUM"

    assert records[0]["proposal_action"] == "WAIT"
    assert records[0]["proposal_status"] == "REJECTED"
    assert records[0]["proposal_reason"] == "Monitoring"

    assert records[0]["action"] == "HOLD"
    assert records[0]["execution_status"] is None
    assert records[0]["realized_pnl"] == 0.0

    assert records[0]["position_side"] is None
    assert records[0]["entry_price"] is None
    assert records[0]["quantity"] is None

    serialized = json.dumps(records)

    assert isinstance(serialized, str)

def test_paper_market_cycle_runner_executes_end_to_end_scenario():

    class SequencedIntelligenceFlow:

        def __init__(self):
            self.calls = 0

        def create_report(self, consensus):
            self.calls += 1

            actions = {
                1: "BUY",
                2: "WAIT",
                3: "SELL"
            }

            action = actions[self.calls]

            return SimpleNamespace(
                action_proposal=SimpleNamespace(
                    action=action,
                    status="APPROVED",
                    reason=f"Scenario {action}",
                    symbol="BTCUSDT"
                )
            )

    class ScenarioExchangeManager:

        def __init__(self):
            self.prices = [
                65000.0,
                65500.0,
                66000.0
            ]
            self.calls = 0

        def get_price(self, symbol):
            price = self.prices[self.calls]
            self.calls += 1
            return price

    class ScenarioMultiTimeframePipeline:

        def analyze(self, symbol):
            return SimpleNamespace(
                signal="BUY"
            )

    session = PaperTradingSession(
        initial_balance=1000,
        position_size_percent=10
    )

    runner = PaperMarketCycleRunner(
        exchange_manager=ScenarioExchangeManager(),
        multi_timeframe_pipeline=(
            ScenarioMultiTimeframePipeline()
        ),
        intelligence_flow=SequencedIntelligenceFlow(),
        session=session
    )

    results = runner.run(
        cycle_count=3,
        symbol="BTCUSDT"
    )

    records = runner.build_cycle_records(
        results
    )

    assert len(results) == 3
    assert len(records) == 3

    assert results[0]["action"] == "OPEN"
    assert results[1]["action"] == "HOLD"
    assert results[2]["action"] == "CLOSE"

    assert records[0]["action"] == "OPEN"
    assert records[1]["action"] == "HOLD"
    assert records[2]["action"] == "CLOSE"

    assert records[0]["price"] == 65000.0
    assert records[1]["price"] == 65500.0
    assert records[2]["price"] == 66000.0

    assert records[0]["proposal_action"] == "BUY"
    assert records[1]["proposal_action"] == "WAIT"
    assert records[2]["proposal_action"] == "SELL"

    assert records[0]["proposal_status"] == "APPROVED"
    assert records[1]["proposal_status"] == "APPROVED"
    assert records[2]["proposal_status"] == "APPROVED"

    assert results[0]["position"] is not None
    assert results[1]["position"] is not None
    assert results[2]["position"] is not None

    assert results[0]["realized_pnl"] == 0.0
    assert results[1]["realized_pnl"] == 0.0

    assert results[2]["realized_pnl"] > 0

    assert session.get_position() is None
    assert session.get_trade_count() == 1
    assert session.get_total_pnl() > 0
    assert session.get_balance() > 1000

    assert records[0]["execution_status"] == "EXECUTED"
    assert records[1]["execution_status"] is None
    assert records[2]["execution_status"] is None

    assert records[0]["position_side"] == "BUY"
    assert records[0]["entry_price"] == 65000.0
    assert records[0]["quantity"] > 0

    assert records[1]["position_side"] == "BUY"
    assert records[1]["entry_price"] == 65000.0
    assert records[1]["quantity"] == records[0]["quantity"]

    assert records[2]["position_side"] == "BUY"
    assert records[2]["entry_price"] == 65000.0
    assert records[2]["quantity"] == records[0]["quantity"]

    assert records[0]["report"] is not None

    assert (
        records[0]["report"]
        is runner.last_cycle_inputs[0]["report"]
    )

def test_builds_session_record():
    session = PaperTradingSession(
        initial_balance=1000,
        position_size_percent=10
    )

    runner = PaperMarketCycleRunner(
        exchange_manager=FakeExchangeManager(),
        multi_timeframe_pipeline=FakeMultiTimeframePipeline(),
        intelligence_flow=FakeIntelligenceFlow(),
        session=session
    )

    results = runner.run(
        cycle_count=1,
        symbol="BTCUSDT"
    )

    session_record = runner.build_session_record(
        results
    )

    assert "cycles" in session_record
    assert "summary" in session_record
    assert "final_position" in session_record

    assert len(
        session_record["cycles"]
    ) == 1

    assert (
        session_record["summary"]["cycles_processed"]
        == 1
    )

    assert (
        session_record["final_position"]
        == session_record["summary"]["current_position"]
    )

def test_session_record_is_json_serializable():
    session = PaperTradingSession(
        initial_balance=1000,
        position_size_percent=10
    )

    runner = PaperMarketCycleRunner(
        exchange_manager=FakeExchangeManager(),
        multi_timeframe_pipeline=FakeMultiTimeframePipeline(),
        intelligence_flow=FakeIntelligenceFlow(),
        session=session
    )

    results = runner.run(
        cycle_count=1,
        symbol="BTCUSDT"
    )

    session_record = runner.build_session_record(
        results
    )

    serialized = json.dumps(
        session_record
    )

    assert isinstance(
        serialized,
        str
    )

def test_paper_market_cycle_runner_builds_serializable_e2e_records():

    class SequencedIntelligenceFlow:

        def __init__(self):
            self.calls = 0

        def create_report(self, consensus):
            self.calls += 1

            actions = {
                1: "BUY",
                2: "WAIT",
                3: "SELL"
            }

            action = actions[self.calls]

            return SimpleNamespace(
                action_proposal=SimpleNamespace(
                    action=action,
                    status="APPROVED",
                    reason=f"Scenario {action}",
                    symbol="BTCUSDT"
                )
            )

    class ScenarioExchangeManager:

        def __init__(self):
            self.prices = [
                65000.0,
                65500.0,
                66000.0
            ]
            self.calls = 0

        def get_price(self, symbol):
            price = self.prices[self.calls]
            self.calls += 1
            return price

    class ScenarioMultiTimeframePipeline:

        def analyze(self, symbol):
            return SimpleNamespace(
                signal="BUY"
            )

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    runner = PaperMarketCycleRunner(
        exchange_manager=ScenarioExchangeManager(),
        multi_timeframe_pipeline=(
            ScenarioMultiTimeframePipeline()
        ),
        intelligence_flow=SequencedIntelligenceFlow(),
        session=session
    )

    results = runner.run(
        cycle_count=3,
        symbol="BTCUSDT"
    )

    records = (
        runner.build_serializable_cycle_records(
            results
        )
    )

    assert len(records) == 3

    assert records[0]["action"] == "OPEN"
    assert records[1]["action"] == "HOLD"
    assert records[2]["action"] == "CLOSE"

    assert records[0]["proposal_action"] == "BUY"
    assert records[1]["proposal_action"] == "WAIT"
    assert records[2]["proposal_action"] == "SELL"

    assert records[0]["execution_status"] == "EXECUTED"
    assert records[1]["execution_status"] is None
    assert records[2]["execution_status"] is None

    assert records[0]["position_side"] == "BUY"
    assert records[1]["position_side"] == "BUY"
    assert records[2]["position_side"] == "BUY"

    assert records[0]["entry_price"] == 65000.0
    assert records[1]["entry_price"] == 65000.0
    assert records[2]["entry_price"] == 65000.0

    assert records[0]["quantity"] > 0
    assert records[1]["quantity"] == records[0]["quantity"]
    assert records[2]["quantity"] == records[0]["quantity"]

    assert records[0]["realized_pnl"] == 0.0
    assert records[1]["realized_pnl"] == 0.0
    assert records[2]["realized_pnl"] > 0

    serialized = json.dumps(records)

    assert isinstance(serialized, str)

def test_serializes_session_from_runner():
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    runner = PaperMarketCycleRunner(
        exchange_manager=FakeExchangeManager(),
        multi_timeframe_pipeline=(
            FakeMultiTimeframePipeline()
        ),
        intelligence_flow=FakeIntelligenceFlow(),
        session=session
    )

    results = runner.run(
        cycle_count=3,
        symbol="BTCUSDT"
    )

    serialized = runner.serialize_session(
        results
    )

    restored = json.loads(
        serialized
    )

    assert restored["summary"]["cycles_processed"] == 3
    assert restored["summary"]["hold_count"] == 3
    assert restored["summary"]["open_count"] == 0
    assert restored["summary"]["close_count"] == 0

    assert restored["summary"]["balance"] == 1000.0
    assert restored["summary"]["total_pnl"] == 0.0
    assert restored["summary"]["trade_count"] == 0

    assert restored["final_position"] is None

    assert len(
        restored["cycles"]
    ) == 3

    assert restored["cycles"][0]["cycle"] == 1
    assert restored["cycles"][0]["symbol"] == "BTCUSDT"
    assert restored["cycles"][0]["action"] == "HOLD"
def test_paper_market_cycle_runner_persists_session_archive(tmp_path):

    from execution.paper_session_archive import PaperSessionArchive

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    archive = PaperSessionArchive(
        root_path=tmp_path
    )

    runner = PaperMarketCycleRunner(
        exchange_manager=FakeExchangeManager(),
        multi_timeframe_pipeline=FakeMultiTimeframePipeline(),
        intelligence_flow=FakeIntelligenceFlow(),
        session=session,
        session_archive=archive
    )

    results = runner.run(
        cycle_count=3,
        symbol="BTCUSDT"
    )

    saved_record = runner.save_session(
        results
    )

    assert saved_record["summary"]["cycles_processed"] == 3
    assert saved_record["summary"]["trade_count"] == 0
    assert saved_record["summary"]["balance"] == 1000.0

    assert archive.list() == [
        session.session_id
    ]

    restored = archive.load(
        session.session_id
    )

    assert restored["summary"]["cycles_processed"] == 3
    assert restored["summary"]["hold_count"] == 3
    assert restored["summary"]["balance"] == 1000.0
    assert restored["final_position"] is None

class FakeMarketDataPipeline:

    def __init__(self):
        self.calls = 0

    def fetch_multi_timeframes(
        self,
        symbol="BTCUSDT",
        timeframes=None
    ):
        self.calls += 1

        return {
            "1m": None,
            "30m": None,
            "4H": None,
            "1D": None
        }


def test_paper_market_cycle_runner_refreshes_market_data_each_cycle():
    exchange_manager = FakeExchangeManager()
    market_data_pipeline = FakeMarketDataPipeline()
    pipeline = FakeMultiTimeframePipeline()
    intelligence_flow = FakeIntelligenceFlow()

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    runner = PaperMarketCycleRunner(
        exchange_manager=exchange_manager,
        multi_timeframe_pipeline=pipeline,
        intelligence_flow=intelligence_flow,
        session=session,
        market_data_pipeline=market_data_pipeline
    )

    results = runner.run(
        cycle_count=3,
        symbol="BTCUSDT"
    )

    assert len(results) == 3
    assert market_data_pipeline.calls == 3
    assert pipeline.calls == 3
    assert intelligence_flow.calls == 3

def test_paper_market_cycle_runner_persists_changing_market_data(tmp_path):
    from core.database import DatabaseManager
    from core.market_data.pipeline import MarketDataPipeline
    from exchanges.mock_exchange import MockExchange

    database = DatabaseManager(
        str(tmp_path / "market_data.db")
    )
    database.connect()

    exchange = MockExchange()

    exchange.set_candle_sequence(
        "BTCUSDT",
        "1m",
        [
            {
                "timestamp": 1752364800,
                "open": 64950,
                "high": 65100,
                "low": 64800,
                "close": 65000,
                "volume": 125.5
            },
            {
                "timestamp": 1752364860,
                "open": 65450,
                "high": 65600,
                "low": 65300,
                "close": 65500,
                "volume": 130.5
            },
            {
                "timestamp": 1752364920,
                "open": 65950,
                "high": 66100,
                "low": 65800,
                "close": 66000,
                "volume": 135.5
            }
        ]
    )

    market_data_pipeline = MarketDataPipeline(
        exchange,
        database
    )

    pipeline = FakeMultiTimeframePipeline()
    intelligence_flow = FakeIntelligenceFlow()

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    runner = PaperMarketCycleRunner(
        exchange_manager=exchange,
        multi_timeframe_pipeline=pipeline,
        intelligence_flow=intelligence_flow,
        session=session,
        market_data_pipeline=market_data_pipeline
    )

    results = runner.run(
        cycle_count=3,
        symbol="BTCUSDT"
    )

    assert len(results) == 3

    candles = database.get_candles()

    btc_1m = [
        candle
        for candle in candles
        if candle[1] == "BTCUSDT"
        and candle[2] == "1m"
    ]

    assert len(btc_1m) == 3

    btc_1m = sorted(
        btc_1m,
        key=lambda candle: candle[3]
    )

    assert [
        candle[3]
        for candle in btc_1m
    ] == [
        1752364800,
        1752364860,
        1752364920
    ]

    assert [
        candle[7]
        for candle in btc_1m
    ] == [
        65000,
        65500,
        66000
    ]

    database.close()
