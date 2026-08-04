from intelligence.memory.outcome_memory import OutcomeMemory
from intelligence.outcome_record import OutcomeRecord


def test_outcome_memory_stores_outcomes():

    memory = OutcomeMemory()

    outcome = OutcomeRecord(
        decision="LONG",
        entry_price=65000,
        exit_price=67000
    )

    memory.save_outcome(
        outcome
    )

    records = memory.get_outcomes()

    assert len(records) == 1

    assert records[0].entry_price == 65000