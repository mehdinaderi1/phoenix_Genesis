from types import SimpleNamespace

from core.market_data.operational_market_context import OperationalMarketContext
from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from execution.paper_session_archive import PaperSessionArchive
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession


class ControlledMarketRuntime:
    def __init__(self):
        self.calls = 0
        self.prices = [65000.0, 65500.0, 66000.0]

    def run_cycle(self, symbol="BTCUSDT"):
        price = self.prices[self.calls]
        self.calls += 1

        observation = SimpleNamespace(
            symbol=symbol,
            price=price,
            source="mock",
            fallback_used=False,
            source_status="HEALTHY"
        )

        context = OperationalMarketContext(
            symbol=symbol,
            trend="BULLISH",
            signal="BUY",
            confidence=85.0,
            timestamp="2026-09-14T00:00:00+00:00"
        )

        return {
            "observation": observation,
            "context": context
        }


class ControlledIntelligenceFlow:
    def __init__(self):
        self.calls = 0
        self.actions = ("PREPARE_LONG", "WAIT", "PREPARE_SHORT")

    def create_report(self, consensus):
        action = self.actions[self.calls]
        self.calls += 1

        decision = SimpleNamespace(
            action=action,
            reason="archive test",
            confidence=85.0,
            strategy={"name": "ARCHIVE_TEST_STRATEGY"}
        )

        action_proposal = SimpleNamespace(
            action=action,
            status="APPROVED",
            reason="archive test",
            confidence=85.0,
            symbol="BTCUSDT",
            strategy={"name": "ARCHIVE_TEST_STRATEGY"},
            risk_status="LOW",
            metadata={}
        )

        return SimpleNamespace(
            decision=decision,
            action_proposal=action_proposal
        )


class FaultyMarketRuntime:
    def __init__(self):
        self.calls = 0

    def run_cycle(self, symbol="BTCUSDT"):
        self.calls += 1

        if self.calls == 2:
            raise RuntimeError("temporary market failure")

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
            timestamp="2026-09-14T00:00:00+00:00"
        )

        return {
            "observation": observation,
            "context": context
        }


class StableIntelligenceFlow:
    def create_report(self, consensus):
        decision = SimpleNamespace(
            action="WAIT",
            reason="test",
            confidence=85.0
        )

        action_proposal = SimpleNamespace(
            action="WAIT",
            status="APPROVED",
            reason="test",
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


def test_operational_paper_runtime_persists_session_archive(tmp_path):
    market_runtime = ControlledMarketRuntime()
    intelligence = ControlledIntelligenceFlow()
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0
    )
    paper_runtime = PaperTradingRuntime(session)
    archive = PaperSessionArchive(tmp_path / "paper_sessions")

    runtime = OperationalPaperRuntime(
        market_runtime,
        intelligence,
        paper_runtime,
        session_archive=archive
    )

    results = runtime.run(cycles=3)

    assert len(results) == 3
    assert results[0]["paper_result"]["action"] == "OPEN"
    assert results[1]["paper_result"]["action"] == "HOLD"
    assert results[2]["paper_result"]["action"] == "CLOSE"

    session_id = session.session_id
    assert session_id in archive.list()

    saved = archive.load(session_id)

    assert saved["session_id"] == session_id
    assert saved["summary"]["balance"] > 1000.0
    assert saved["summary"]["trade_count"] == 1
    assert saved["summary"]["total_pnl"] > 0
    assert len(saved["cycles"]) == 3


def test_operational_paper_runtime_archives_session_after_error_cycle(tmp_path):
    market_runtime = FaultyMarketRuntime()
    intelligence = StableIntelligenceFlow()
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0
    )
    paper_runtime = PaperTradingRuntime(session)
    archive = PaperSessionArchive(tmp_path / "paper_sessions")

    runtime = OperationalPaperRuntime(
        market_runtime,
        intelligence,
        paper_runtime,
        session_archive=archive
    )

    results = runtime.run(
        cycles=3,
        continue_on_error=True
    )

    assert len(results) == 3
    assert results[1]["error"] is not None
    assert results[1]["paper_result"] is None

    session_id = session.session_id
    assert session_id in archive.list()

    saved = archive.load(session_id)

    assert saved["session_id"] == session_id
    assert saved["summary"]["balance"] == 1000.0
    assert saved["summary"]["trade_count"] == 0
    assert saved["summary"]["total_pnl"] == 0.0
    assert len(saved["cycles"]) == 3

from execution.paper_session_manager import PaperSessionManager


def test_operational_paper_runtime_builds_session_report(tmp_path):
    market_runtime = ControlledMarketRuntime()
    intelligence = ControlledIntelligenceFlow()
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0
    )
    paper_runtime = PaperTradingRuntime(session)
    archive = PaperSessionArchive(tmp_path / "paper_sessions")

    runtime = OperationalPaperRuntime(
        market_runtime,
        intelligence,
        paper_runtime,
        session_archive=archive
    )

    results = runtime.run(cycles=3)

    manager = PaperSessionManager(archive)
    report = manager.get_session_report(session.session_id)

    assert report["session_id"] == session.session_id
    assert report["cycles"] == 3
    assert report["trade_count"] == 1
    assert report["win_count"] == 1
    assert report["loss_count"] == 0
    assert report["win_rate"] == 100.0
    assert report["total_pnl"] > 0
