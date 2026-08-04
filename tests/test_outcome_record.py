from intelligence.outcome_record import OutcomeRecord


def test_outcome_record_stores_market_reality():

    decision = "LONG"

    outcome = OutcomeRecord(
        decision=decision,
        entry_price=65000,
        exit_price=67000
    )

    assert outcome.decision == decision

    assert outcome.entry_price == 65000

    assert outcome.exit_price == 67000

    assert hasattr(
        outcome,
        "timestamp"
    )