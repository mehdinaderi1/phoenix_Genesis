from intelligence.decision_history import DecisionHistory
from intelligence.decision_record import DecisionRecord


def test_decision_history():

    history = DecisionHistory()


    record = DecisionRecord(
        symbol="BTCUSDT",
        timeframe="Multi",
        regime="TRENDING",
        signal="BUY",
        confidence=85,
        risk="LOW",
        action="PREPARE_LONG",
        validation_status="APPROVED"
    )


    history.add(record)


    assert len(history.get_all()) == 1


    latest = history.get_latest()


    assert latest.symbol == "BTCUSDT"
    assert latest.action == "PREPARE_LONG"