from intelligence.strategy_consensus_explanation import (
    StrategyConsensusExplanation
)



def test_strategy_consensus_explanation_contract():

    explanation = StrategyConsensusExplanation(

        decision="BUY",

        dominant_strategy="momentum_v2",

        supporting_strategies=[
            "momentum_v2",
            "trend_following"
        ],

        opposing_strategies=[
            "mean_reversion"
        ],

        reasons=[
            "Majority strategies agree",
            "Confidence above threshold"
        ],

        confidence=0.85,

        conflict_detected=True
    )



    data = explanation.to_dict()



    assert data["decision"] == "BUY"

    assert (
        data["dominant_strategy"]
        ==
        "momentum_v2"
    )


    assert len(
        data["supporting_strategies"]
    ) == 2


    assert (
        data["conflict_detected"]
        is True
    )


    assert (
        data["confidence"]
        ==
        0.85
    )