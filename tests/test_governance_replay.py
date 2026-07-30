from intelligence.governance.governance_replay import (
    GovernanceReplay
)

from intelligence.governance.governance_history import (
    GovernanceHistory
)

from intelligence.governance.governance_record import (
    GovernanceRecord
)



def test_governance_replay_trust():


    history = GovernanceHistory()


    history.store(
        GovernanceRecord(
            strategy={
                "name": "Trend"
            },
            status="APPROVED",
            reason="Good",
            result="SUCCESS"
        )
    )


    history.store(
        GovernanceRecord(
            strategy={
                "name": "Trend"
            },
            status="APPROVED",
            reason="Good",
            result="SUCCESS"
        )
    )


    replay = GovernanceReplay(
        history
    )


    result = replay.replay(
        "Trend"
    )


    assert result["recommendation"] == "TRUST"
    assert result["history_count"] == 2



def test_governance_replay_unknown():


    replay = GovernanceReplay()


    result = replay.replay(
        "Unknown"
    )


    assert result["recommendation"] == "UNKNOWN"