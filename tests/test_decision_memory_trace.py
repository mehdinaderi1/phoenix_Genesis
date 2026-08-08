from intelligence.decision_memory import DecisionMemory
from intelligence.decision_record import DecisionRecord


def test_decision_memory_stores_trace():

    memory = DecisionMemory()

    record = DecisionRecord(
        symbol="BTCUSDT",
        timeframe="30m",
        regime="TREND",
        signal="BUY",
        confidence=85,
        risk="LOW",
        action="PREPARE_LONG",
        validation_status="APPROVED",
        trace={
            "decision": "PREPARE_LONG",
            "gates": {
                "consensus": True
            }
        }
    )

    memory.store(record)

    saved = memory.get_latest()

    assert saved.trace["decision"] == "PREPARE_LONG"

    assert saved.trace["gates"]["consensus"] is True