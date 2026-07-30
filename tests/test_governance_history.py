from intelligence.governance.governance_history import (
    GovernanceHistory
)


def test_governance_history_store():

    history = GovernanceHistory()


    history.store(
        {
            "strategy": "strategy_alpha",
            "confidence": 10
        }
    )


    assert history.count() == 1



def test_governance_history_retrieve():

    history = GovernanceHistory()


    history.store(
        {
            "strategy": "strategy_alpha",
            "confidence": 10
        }
    )


    records = history.get_all()


    assert records[0]["confidence"] == 10