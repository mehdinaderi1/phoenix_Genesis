from intelligence.strategy_consensus_validator import (
    StrategyConsensusValidator
)


def test_consensus_allows_majority_decision():

    validator = StrategyConsensusValidator()


    consensus = {
        "decision": "BUY",
        "supporting_strategies": 2,
        "opposing_strategies": 1
    }


    result = validator.validate(
        consensus
    )


    assert result is True



def test_consensus_blocks_failed_majority():

    validator = StrategyConsensusValidator()


    consensus = {
        "decision": "BUY",
        "supporting_strategies": 1,
        "opposing_strategies": 2
    }


    result = validator.validate(
        consensus
    )


    assert result is False