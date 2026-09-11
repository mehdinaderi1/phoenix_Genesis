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
    assert records[0]["action"] == "HOLD"
    assert records[0]["realized_pnl"] == 0.0
    assert records[0]["position"] is None

    assert records[1]["cycle"] == 2
    assert records[2]["cycle"] == 3

    assert all(
        record["action"] == "HOLD"
        for record in records
    )

def test_paper_market_cycle_runner_executes_end_to_end_scenario():

    from types import SimpleNamespace

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

    from execution.paper_trading_session import (
        PaperTradingSession
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