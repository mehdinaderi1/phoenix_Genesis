from types import SimpleNamespace

from core.market_data.operational_market_context import (
    OperationalMarketContext
)
from core.market_data.operational_paper_runtime import (
    OperationalPaperRuntime
)


class FakeMarketContextRuntime:
    def __init__(self):
        self.calls = []

    def run_cycle(
        self,
        symbol="BTCUSDT",
        timeframes=None
    ):
        self.calls.append((
            symbol,
            timeframes
        ))

        observation = SimpleNamespace(
            symbol=symbol,
            price=65000.0,
            source="mock",
            fallback_used=False,
            source_status="HEALTHY"
        )

        context = OperationalMarketContext(
            symbol=symbol,
            trend="BULLISH",
            signal="BUY",
            confidence=85.0,
            timestamp="2026-09-13T00:00:00+00:00"
        )

        return {
            "observation": observation,
            "context": context,
            "candle_boundaries": {
                "5m": {
                    "timeframe": "5m",
                    "candle_start": 1790111100,
                    "next_boundary": 1790111400,
                    "duration_seconds": 300,
                    "age_seconds": 100,
                    "is_closed": False
                }
            }
        }


class FakeIntelligenceFlow:
    def __init__(self):
        self.consensuses = []

    def create_report(self, consensus):
        self.consensuses.append(consensus)

        decision = SimpleNamespace(action="BUY")
        proposal = SimpleNamespace(action="BUY")

        return SimpleNamespace(
            decision=decision,
            action_proposal=proposal
        )


class FakePaperTradingRuntime:
    def __init__(self):
        self.cycles = []

    def run(self, cycles, symbol="BTCUSDT"):
        self.cycles.extend(cycles)

        return [{
            "action": "OPEN",
            "position": SimpleNamespace(
                side="BUY",
                entry_price=cycles[0]["price"]
            ),
            "realized_pnl": 0.0,
            "learning_result": None
        }]


def test_operational_paper_runtime_connects_market_intelligence_and_paper():
    market_runtime = FakeMarketContextRuntime()
    intelligence = FakeIntelligenceFlow()
    paper_runtime = FakePaperTradingRuntime()

    runtime = OperationalPaperRuntime(
        market_runtime,
        intelligence,
        paper_runtime
    )

    results = runtime.run(cycles=2)

    assert len(results) == 2
    assert len(intelligence.consensuses) == 2
    assert len(paper_runtime.cycles) == 2

    assert market_runtime.calls == [
        ("BTCUSDT", None),
        ("BTCUSDT", None),
    ]

    assert paper_runtime.cycles[0]["price"] == 65000.0
    assert paper_runtime.cycles[0]["symbol"] == "BTCUSDT"
    assert paper_runtime.cycles[0]["decision"].action == "BUY"
    assert paper_runtime.cycles[0]["action_proposal"].action == "BUY"

    assert results[0]["paper_result"]["action"] == "OPEN"
    assert results[0]["paper_result"]["position"].entry_price == 65000.0

    assert results[0]["candle_boundaries"]["5m"]["timeframe"] == "5m"
    assert results[0]["candle_boundaries"]["5m"]["candle_start"] == 1790111100
    assert results[0]["candle_boundaries"]["5m"]["next_boundary"] == 1790111400
    assert results[0]["candle_boundaries"]["5m"]["age_seconds"] == 100
    assert results[0]["candle_boundaries"]["5m"]["is_closed"] is False


def test_operational_paper_runtime_propagates_custom_timeframes():
    market_runtime = FakeMarketContextRuntime()
    intelligence = FakeIntelligenceFlow()
    paper_runtime = FakePaperTradingRuntime()

    runtime = OperationalPaperRuntime(
        market_runtime,
        intelligence,
        paper_runtime
    )

    timeframes = ("5m", "15m", "30m", "4H", "1D")

    results = runtime.run(
        cycles=2,
        timeframes=timeframes
    )

    assert len(results) == 2

    assert market_runtime.calls == [
        ("BTCUSDT", timeframes),
        ("BTCUSDT", timeframes),
    ]

    assert results[0]["candle_boundaries"]["5m"]["timeframe"] == "5m"


def test_operational_paper_runtime_rejects_missing_dependencies():
    intelligence = FakeIntelligenceFlow()
    paper_runtime = FakePaperTradingRuntime()

    try:
        OperationalPaperRuntime(
            None,
            intelligence,
            paper_runtime
        )
    except ValueError as exc:
        assert str(exc) == "market_context_runtime must not be None"
    else:
        raise AssertionError("Expected ValueError")

    try:
        OperationalPaperRuntime(
            FakeMarketContextRuntime(),
            None,
            paper_runtime
        )
    except ValueError as exc:
        assert str(exc) == "intelligence_flow must not be None"
    else:
        raise AssertionError("Expected ValueError")

    try:
        OperationalPaperRuntime(
            FakeMarketContextRuntime(),
            intelligence,
            None
        )
    except ValueError as exc:
        assert str(exc) == "paper_trading_runtime must not be None"
    else:
        raise AssertionError("Expected ValueError")


class FakeExecutionRuntime:
    def __init__(self):
        self.cycles = []

    def run(self, cycles, symbol="BTCUSDT"):
        self.cycles.extend(cycles)

        return [{
            "action": "EXECUTION_BOUNDARY",
            "position": None,
            "realized_pnl": 0.0,
            "learning_result": None
        }]


def test_operational_paper_runtime_uses_injected_execution_runtime():
    market_runtime = FakeMarketContextRuntime()
    intelligence = FakeIntelligenceFlow()
    paper_runtime = FakePaperTradingRuntime()
    execution_runtime = FakeExecutionRuntime()

    runtime = OperationalPaperRuntime(
        market_runtime,
        intelligence,
        paper_runtime,
        execution_runtime=execution_runtime
    )

    results = runtime.run(cycles=2)

    assert len(execution_runtime.cycles) == 2
    assert len(paper_runtime.cycles) == 0

    assert results[0]["paper_result"]["action"] == (
        "EXECUTION_BOUNDARY"
    )


class FakeOpportunityObserver:
    def __init__(self, should_fail=False):
        self.calls = []
        self.should_fail = should_fail

    def observe(self, report, decision=None, **kwargs):
        self.calls.append((report, decision))

        if self.should_fail:
            raise RuntimeError("observer failure")

        return {
            "symbol": (
                getattr(report, "symbol", None)
                or kwargs.get("symbol")
            ),
            "decision": decision.action,
            "execution_attempted": False,
        }


def test_runtime_records_opportunity_from_existing_decision():
    market_runtime = FakeMarketContextRuntime()
    intelligence = FakeIntelligenceFlow()
    paper_runtime = FakePaperTradingRuntime()
    observer = FakeOpportunityObserver()

    runtime = OperationalPaperRuntime(
        market_runtime,
        intelligence,
        paper_runtime,
        opportunity_observer=observer,
    )

    results = runtime.run(cycles=1)

    assert len(observer.calls) == 1
    report, decision = observer.calls[0]
    assert decision is report.decision
    assert results[0]["opportunity_observation_error"] is None, (
        results[0]["opportunity_observation_error"]
    )

    assert results[0]["opportunity"]["symbol"] == "BTCUSDT"
    assert results[0]["opportunity"]["decision"] == "BUY"
    assert results[0]["opportunity"]["execution_attempted"] is False
    assert results[0]["paper_result"]["action"] == "OPEN"


def test_runtime_continues_paper_when_opportunity_observer_fails():
    market_runtime = FakeMarketContextRuntime()
    intelligence = FakeIntelligenceFlow()
    paper_runtime = FakePaperTradingRuntime()
    observer = FakeOpportunityObserver(should_fail=True)

    runtime = OperationalPaperRuntime(
        market_runtime,
        intelligence,
        paper_runtime,
        opportunity_observer=observer,
    )

    results = runtime.run(cycles=1)

    assert len(paper_runtime.cycles) == 1
    assert results[0]["paper_result"]["action"] == "OPEN"
    assert results[0]["opportunity"] is None
    assert results[0]["opportunity_observation_error"] == (
        "RuntimeError: observer failure"
    )
