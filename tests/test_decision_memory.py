from intelligence.decision_memory import DecisionMemory
from intelligence.decision_record import DecisionRecord


def test_decision_memory_store():

    memory = DecisionMemory()

    record = DecisionRecord(
        symbol="BTCUSDT",
        timeframe="30m",
        regime="TRENDING",
        signal="BUY",
        confidence=85,
        risk="LOW",
        action="PREPARE_LONG",
        validation_status="APPROVED"
    )


    memory.store(record)


    assert memory.count() == 1

    assert memory.get_latest().action == "PREPARE_LONG"

    assert memory.get_latest().confidence == 85