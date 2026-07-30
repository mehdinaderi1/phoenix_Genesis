from intelligence.strategy_governance import StrategyGovernance


class MockDecisionEngine:

    def __init__(self):
        self.called = False


    def run(
        self,
        strategy
    ):

        self.called = True

        return {
            "action": "LONG",
            "confidence": 90
        }



def test_intelligence_flow_allows_governed_strategy():

    governance = StrategyGovernance()

    decision_engine = MockDecisionEngine()


    strategy = {
        "name": "strong_strategy",
        "score": 90,
        "confidence": 85,
        "risk": "LOW"
    }


    governance_result = governance.evaluate(
        strategy
    )


    assert governance_result["status"] == "APPROVED"


    if governance_result["status"] == "APPROVED":

        decision = decision_engine.run(
            strategy
        )

    else:
        decision = None


    assert decision is not None
    assert decision_engine.called is True



def test_intelligence_flow_blocks_rejected_strategy():

    governance = StrategyGovernance()

    decision_engine = MockDecisionEngine()


    strategy = {
        "name": "dangerous_strategy",
        "score": 95,
        "confidence": 90,
        "risk": "HIGH"
    }


    governance_result = governance.evaluate(
        strategy
    )


    assert governance_result["status"] == "REJECTED"


    if governance_result["status"] == "APPROVED":

        decision_engine.run(
            strategy
        )


    assert decision_engine.called is False