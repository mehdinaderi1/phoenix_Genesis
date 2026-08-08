from intelligence.decision_trace import DecisionTrace


def test_decision_trace_contract():

    trace = DecisionTrace(

        decision="PREPARE_LONG",

        signal="BUY",

        confidence=85,

        risk="LOW",

        strategy_consensus={
            "supporting": 3,
            "opposing": 1
        },

        gates={
            "strategy": True,
            "consensus": True
        },

        explanation={
            "reason": "strong consensus"
        }
    )


    data = trace.to_dict()


    assert data["decision"] == "PREPARE_LONG"

    assert data["gates"]["consensus"] is True

    assert data["explanation"]["reason"] == (
        "strong consensus"
    )