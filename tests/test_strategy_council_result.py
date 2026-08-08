from intelligence.strategy_council_result import (
    StrategyCouncilResult
)


def test_strategy_council_result_creation():

    result = StrategyCouncilResult(
        strategies=[
            "momentum_strategy",
            "breakout_strategy"
        ],
        strategy_votes=[
            {
                "strategy": "momentum_strategy",
                "action": "BUY",
                "confidence": 0.8
            }
        ],
        consensus_action="BUY",
        consensus_confidence=0.8,
        supporting_strategies=[
            "momentum_strategy"
        ],
        conflicting_strategies=[],
        explanation="Majority strategies support BUY"
    )


    assert result.consensus_action == "BUY"

    assert result.consensus_confidence == 0.8

    assert (
        "momentum_strategy"
        in result.supporting_strategies
    )



def test_strategy_council_result_to_dict():

    result = StrategyCouncilResult(
        consensus_action="SELL"
    )


    data = result.to_dict()


    assert data["consensus_action"] == "SELL"

    assert "timestamp" in data

    assert "strategy_votes" in data