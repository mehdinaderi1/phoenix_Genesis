from intelligence.governance.governance_history import (
    GovernanceHistory
)

from intelligence.governance.governance_record import (
    GovernanceRecord
)



def test_governance_history_store():

    history = GovernanceHistory()


    record = GovernanceRecord(
        strategy={
            "name": "Trend"
        },
        status="APPROVED",
        reason="High confidence evolution"
    )


    history.store(
        record
    )


    assert history.count() == 1



def test_governance_history_latest():

    history = GovernanceHistory()


    history.store(
        GovernanceRecord(
            strategy={
                "name": "Trend"
            },
            status="APPROVED",
            reason="Stable"
        )
    )


    latest = history.latest()


    assert latest["status"] == "APPROVED"



def test_governance_history_find_strategy():

    history = GovernanceHistory()


    history.store(
        GovernanceRecord(
            strategy={
                "name": "Trend"
            },
            status="APPROVED",
            reason="Good performance"
        )
    )


    history.store(
        GovernanceRecord(
            strategy={
                "name": "Random"
            },
            status="BLOCKED",
            reason="Low trust"
        )
    )


    result = history.find_by_strategy(
        "Trend"
    )


    assert len(result) == 1
    assert result[0]["status"] == "APPROVED"



def test_governance_history_blocked_records():

    history = GovernanceHistory()


    history.store(
        GovernanceRecord(
            strategy={
                "name": "Risky"
            },
            status="BLOCKED",
            reason="Governance rejected"
        )
    )


    blocked = history.find_by_status(
        "BLOCKED"
    )


    assert len(blocked) == 1
    assert blocked[0]["reason"] == "Governance rejected"