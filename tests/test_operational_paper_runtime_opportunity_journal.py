from types import SimpleNamespace

from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from core.market_data.operational_market_context import OperationalMarketContext
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession
from intelligence.observation.opportunity_journal import OpportunityJournal


class MarketRuntime:
    def run_cycle(self, symbol="BTCUSDT"):
        return {
            "observation": SimpleNamespace(
                symbol=symbol,
                price=65000.0,
                source="test",
                fallback_used=False,
                source_status="HEALTHY",
                timestamp="2026-10-10T00:00:00+00:00",
            ),
            "context": OperationalMarketContext(
                symbol=symbol,
                trend="BULLISH",
                signal="BUY",
                confidence=85.0,
                timestamp="2026-10-10T00:00:00+00:00",
            ),
        }


class IntelligenceFlow:
    def create_report(self, consensus):
        return SimpleNamespace(
            decision=SimpleNamespace(
                action="WAIT",
                reason="journal test",
                confidence=85.0,
            ),
            action_proposal=SimpleNamespace(
                action="WAIT",
                status="APPROVED",
                reason="journal test",
                confidence=85.0,
                symbol="BTCUSDT",
                strategy=None,
                risk_status="LOW",
                metadata={},
            ),
        )


class Observer:
    def observe(self, report, decision=None, **kwargs):
        return {
            "symbol": kwargs["symbol"],
            "decision": decision.action,
            "reference_price": kwargs["reference_price"],
            "observation_timestamp": kwargs.get("observation_timestamp"),
            "execution_attempted": False,
            "filters": {},
            "blocked_reasons": [],
        }


class FailingJournal:
    def append(self, record):
        raise OSError("journal unavailable")


def make_runtime(observer, journal=None):
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0,
    )
    return OperationalPaperRuntime(
        MarketRuntime(),
        IntelligenceFlow(),
        PaperTradingRuntime(session),
        opportunity_observer=observer,
        opportunity_journal=journal,
    )


def test_runtime_appends_observed_opportunity_to_journal(tmp_path):
    journal = OpportunityJournal(tmp_path / "opportunities.jsonl")
    runtime = make_runtime(Observer(), journal)

    results = runtime.run(cycles=1)

    assert results[0]["opportunity"]["symbol"] == "BTCUSDT"
    assert results[0]["opportunity_journal_error"] is None

    records = journal.read_all()
    assert len(records) == 1
    assert records[0]["symbol"] == "BTCUSDT"
    assert records[0]["reference_price"] == 65000.0
    assert records[0]["observation_timestamp"] == (
        "2026-10-10T00:00:00+00:00"
    )
    assert records[0]["execution_attempted"] is False


def test_journal_failure_does_not_stop_paper_runtime():
    runtime = make_runtime(Observer(), FailingJournal())

    results = runtime.run(cycles=1)

    assert len(results) == 1
    assert results[0]["error"] is None
    assert "OSError: journal unavailable" == (
        results[0]["opportunity_journal_error"]
    )
