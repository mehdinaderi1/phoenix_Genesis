from datetime import datetime, timezone

import intelligence.flow as flow_module
from intelligence.flow import IntelligenceFlow


FIXED_NOW = datetime(2026, 10, 14, 12, 0, 0, tzinfo=timezone.utc)


class FixedDateTime:
    @staticmethod
    def now(tz=None):
        if tz is None:
            return FIXED_NOW.replace(tzinfo=None)
        return FIXED_NOW.astimezone(tz)


class MockConsensus:
    trend = "BULLISH"
    signal = "BUY"
    confidence = 85


def test_intelligence_flow_quality(monkeypatch):
    monkeypatch.setattr(flow_module, "datetime", FixedDateTime)

    flow = IntelligenceFlow()
    report = flow.create_report(MockConsensus())

    assert report.signal_timestamp == FIXED_NOW.isoformat()

    records = flow.decision_memory.records
    assert len(records) == 1

    record = records[0]
    assert record.symbol == "BTCUSDT"
    assert record.action is not None
    assert record.quality_score > 0


def test_wait_signal_has_no_signal_timestamp():
    class WaitConsensus:
        trend = "BULLISH"
        signal = "WAIT"
        confidence = 85

    flow = IntelligenceFlow()
    report = flow.create_report(WaitConsensus())

    assert str(report.signal).upper() == "WAIT"
    assert report.signal_timestamp is None
