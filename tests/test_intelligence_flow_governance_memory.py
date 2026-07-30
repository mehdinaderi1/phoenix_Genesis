from intelligence.flow import IntelligenceFlow


def test_governance_memory_in_flow():

    flow = IntelligenceFlow()


    strategy = {
        "score": 90,
        "confidence": 85,
        "risk": "LOW"
    }


    flow.strategy_governance.evaluate(
        strategy
    )


    assert flow.governance_memory is not None