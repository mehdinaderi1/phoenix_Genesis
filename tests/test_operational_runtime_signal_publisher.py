from datetime import datetime, timezone
from types import SimpleNamespace

from core.market_data.operational_paper_runtime import (
    OperationalPaperRuntime,
)
from notifications.signal_outbox import SignalOutbox
from notifications.signal_publisher import SignalPublisher


class MarketRuntime:
    def run_cycle(self, symbol="BTCUSDT", timeframes=None):
        return {
            "observation": SimpleNamespace(
                symbol=symbol,
                price=65000.0,
                timestamp="2026-09-13T00:00:00+00:00",
            ),
            "context": SimpleNamespace(
                symbol=symbol,
                trend="BULLISH",
                signal="BUY",
                confidence=85.0,
                consensus_breakdown=None,
            ),
            "candle_boundaries": {
                "5m": {
                    "timeframe": "5m",
                    "candle_start": 1790111100,
                    "next_boundary": 1790111400,
                    "duration_seconds": 300,
                    "age_seconds": 100,
                    "is_closed": False,
                }
            },
        }


class Intelligence:
    def create_report(self, consensus):
        return SimpleNamespace(
            signal="BUY",
            decision=SimpleNamespace(action="BUY"),
            signal_timestamp="2026-10-14T11:58:30+00:00",
            action_proposal=SimpleNamespace(
                action="BUY",
                status="APPROVED",
                reason="Integration test",
                confidence=0.9,
                risk_status="ACCEPTABLE",
                symbol="BTCUSDT",
                strategy="test",
                metadata={},
            ),
        )


class PaperRuntime:
    def __init__(self):
        self.cycles = []

    def run(self, cycles, symbol="BTCUSDT"):
        self.cycles.extend(cycles)
        return [{"action": "OPEN"}]


def test_runtime_publishes_approved_signal_to_outbox_without_sending(
    tmp_path, monkeypatch
):
    fixed_time = datetime(
        2026, 10, 14, 12, 0, 0, tzinfo=timezone.utc
    )

    class FixedDateTime:
        @staticmethod
        def now(tz=None):
            return fixed_time

    monkeypatch.setattr(
        "core.market_data.operational_paper_runtime.datetime",
        FixedDateTime,
    )

    outbox = SignalOutbox(tmp_path / "notifications.db")
    publisher = SignalPublisher(outbox)

    runtime = OperationalPaperRuntime(
        market_context_runtime=MarketRuntime(),
        intelligence_flow=Intelligence(),
        paper_trading_runtime=PaperRuntime(),
        signal_publisher=publisher,
    )

    results = runtime.run(cycles=2)
    pending = outbox.get_pending_messages()

    assert len(results) == 2
    assert all(result["error"] is None for result in results)
    assert len(pending) == 1
    assert pending[0]["status"] == "PENDING"
    assert "Direction: BUY" in pending[0]["payload"]
    assert "OBSERVE / PAPER" in pending[0]["payload"]

    saved_signal = outbox.get_signal(pending[0]["signal_id"])

    assert saved_signal is not None
    assert saved_signal["generated_at"] == "2026-10-14T11:58:30Z"


def test_publisher_failure_does_not_block_paper_execution():
    class FailingPublisher:
        def publish(
            self,
            proposal,
            observation,
            candle_boundaries,
            generated_at=None,
        ):
            raise RuntimeError("notification storage unavailable")

    paper = PaperRuntime()
    runtime = OperationalPaperRuntime(
        market_context_runtime=MarketRuntime(),
        intelligence_flow=Intelligence(),
        paper_trading_runtime=paper,
        signal_publisher=FailingPublisher(),
    )

    results = runtime.run(cycles=1, continue_on_error=True)

    assert len(results) == 1
    assert results[0]["error"] is None
    assert results[0]["notification_error"] == (
        "RuntimeError: notification storage unavailable"
    )
    assert results[0]["paper_result"]["action"] == "OPEN"
    assert len(paper.cycles) == 1