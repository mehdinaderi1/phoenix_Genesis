from types import SimpleNamespace

from core.market_data.operational_observation_runner import OperationalObservationRunner
from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from core.market_data.operational_market_context import OperationalMarketContext
from execution.paper_session_archive import PaperSessionArchive
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession


class StableMarketRuntime:
    def __init__(self):
        self.calls = 0

    def run(
        self,
        symbol="BTCUSDT",
        cycles=1,
        continue_on_error=False
    ):
        results = []

        for _ in range(cycles):
            self.calls += 1

            observation = SimpleNamespace(
                symbol=symbol,
                price=65000.0 + self.calls * 100.0,
                source="mock",
                fallback_used=False,
                source_status="HEALTHY"
            )

            context = OperationalMarketContext(
                symbol=symbol,
                trend="BULLISH",
                signal="WAIT",
                confidence=85.0,
                timestamp="2026-09-15T00:00:00+00:00"
            )

            results.append({
                "observation": observation,
                "context": context
            })

        return results


class StableIntelligenceFlow:
    def create_report(self, consensus):
        decision = SimpleNamespace(
            action="WAIT",
            reason="integration test",
            confidence=85.0
        )

        action_proposal = SimpleNamespace(
            action="WAIT",
            status="APPROVED",
            reason="integration test",
            confidence=85.0,
            symbol="BTCUSDT",
            strategy=None,
            risk_status="LOW",
            metadata={}
        )

        return SimpleNamespace(
            decision=decision,
            action_proposal=action_proposal
        )


class FakeMarketContextRuntime:
    def __init__(self):
        self.calls = 0
        self.timeframe_calls = []

    def run_cycle(
        self,
        symbol="BTCUSDT",
        timeframes=None
    ):
        self.calls += 1
        self.timeframe_calls.append(timeframes)

        observation = SimpleNamespace(
            symbol=symbol,
            price=65000.0 + self.calls * 100.0,
            source="mock",
            fallback_used=False,
            source_status="HEALTHY"
        )

        context = OperationalMarketContext(
            symbol=symbol,
            trend="BULLISH",
            signal="WAIT",
            confidence=85.0,
            timestamp="2026-09-15T00:00:00+00:00"
        )

        return {
            "observation": observation,
            "context": context
        }


def test_observation_runner_integrates_with_operational_paper_runtime(tmp_path):
    market_runtime = FakeMarketContextRuntime()
    intelligence = StableIntelligenceFlow()
    session = PaperTradingSession()
    paper_runtime = PaperTradingRuntime(session)
    archive = PaperSessionArchive(tmp_path / "paper_sessions")

    operational_runtime = OperationalPaperRuntime(
        market_context_runtime=market_runtime,
        intelligence_flow=intelligence,
        paper_trading_runtime=paper_runtime,
        session_archive=archive
    )

    sleeps = []

    runner = OperationalObservationRunner(
        runtime=operational_runtime,
        sleep_fn=sleeps.append
    )

    timeframes = ("5m", "15m", "30m", "4H", "1D")

    results = runner.run(
        symbol="BTCUSDT",
        cycles=3,
        interval_seconds=5,
        timeframes=timeframes
    )

    assert len(results) == 3
    assert market_runtime.calls == 3
    assert market_runtime.timeframe_calls == [
        timeframes,
        timeframes,
        timeframes
    ]
    assert all(
        result["paper_result"]["action"] == "HOLD"
        for result in results
    )
    assert session.get_position() is None
    assert sleeps == [5, 5]

    saved = archive.load(session.session_id)
    assert saved["summary"]["cycles_processed"] == 3
    assert len(saved["cycles"]) == 3
