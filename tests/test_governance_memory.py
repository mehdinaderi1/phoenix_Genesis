from intelligence.governance.governance_memory import (
    GovernanceMemory
)

from intelligence.governance.governance_record import (
    GovernanceRecord
)


def test_governance_memory_store():

    memory = GovernanceMemory()


    record = GovernanceRecord(
        strategy={
            "name": "momentum_v2"
        },
        status="APPROVED",
        reason="low risk"
    )


    memory.store(
        record
    )


    assert memory.count() == 1



def test_governance_memory_latest():

    memory = GovernanceMemory()


    memory.store(
        GovernanceRecord(
            strategy={
                "name": "test"
            },
            status="REJECTED",
            reason="high risk"
        )
    )


    latest = memory.latest()


    assert latest.status == "REJECTED"