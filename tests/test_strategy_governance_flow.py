from intelligence.strategy_governance import StrategyGovernance


def test_governance_allows_approved_strategy_flow():

    governance = StrategyGovernance()

    strategy = {
        "name": "momentum_v1",
        "score": 90,
        "confidence": 85,
        "risk": "LOW"
    }

    governance_result = governance.evaluate(
        strategy
    )

    assert governance_result["status"] == "APPROVED"



def test_governance_blocks_rejected_strategy_flow():

    governance = StrategyGovernance()

    strategy = {
        "name": "weak_strategy",
        "score": 40,
        "confidence": 30,
        "risk": "HIGH"
    }

    governance_result = governance.evaluate(
        strategy
    )

    assert governance_result["status"] == "REJECTED"



def test_governance_blocks_before_decision_layer():

    governance = StrategyGovernance()

    strategy = {
        "name": "high_risk_strategy",
        "score": 95,
        "confidence": 90,
        "risk": "HIGH"
    }

    governance_result = governance.evaluate(
        strategy
    )

    assert governance_result["status"] != "APPROVED"