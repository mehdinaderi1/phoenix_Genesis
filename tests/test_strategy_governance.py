from intelligence.strategy_governance import StrategyGovernance


def test_governance_approves_strong_strategy():

    governance = StrategyGovernance()

    strategy = {
        "score": 90,
        "confidence": 85,
        "risk": "LOW"
    }

    result = governance.evaluate(
        strategy
    )

    assert result["status"] == "APPROVED"



def test_governance_reviews_medium_strategy():

    governance = StrategyGovernance()

    strategy = {
        "score": 65,
        "confidence": 60,
        "risk": "MEDIUM"
    }

    result = governance.evaluate(
        strategy
    )

    assert result["status"] == "REVIEW"



def test_governance_rejects_bad_strategy():

    governance = StrategyGovernance()

    strategy = {
        "score": 30,
        "confidence": 20,
        "risk": "HIGH"
    }

    result = governance.evaluate(
        strategy
    )

    assert result["status"] == "REJECTED"



def test_governance_rejects_high_risk_strategy():

    governance = StrategyGovernance()

    strategy = {
        "score": 95,
        "confidence": 90,
        "risk": "HIGH"
    }

    result = governance.evaluate(
        strategy
    )

    assert result["status"] == "REJECTED"