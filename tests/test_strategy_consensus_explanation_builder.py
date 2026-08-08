from intelligence.strategy_consensus_explanation_builder import (
    StrategyConsensusExplanationBuilder
)



def test_consensus_explanation_builder():

    builder = StrategyConsensusExplanationBuilder()


    consensus = {

        "decision": "BUY",

        "supporting_strategies": 3,

        "opposing_strategies": 1,

        "confidence": 0.85,

        "top_strategy":
            "momentum_v2"
    }


    result = builder.build(
        consensus
    )


    assert result.decision == "BUY"


    assert (
        result.dominant_strategy
        ==
        "momentum_v2"
    )


    assert (
        result.confidence
        ==
        0.85
    )


    assert (
        "Majority strategies support decision"
        in result.reasons
    )