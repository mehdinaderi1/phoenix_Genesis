from intelligence.strategy_conflict import (
    StrategyConflictResult
)

from intelligence.strategy_conflict_resolver import (
    StrategyConflictResolver
)



def test_resolver_accepts_majority_conflict():

    resolver = StrategyConflictResolver()


    result = StrategyConflictResult(

        conflict=True,

        conflict_level="MEDIUM",

        dominant_action="BUY",

        buy_support=3,

        sell_support=1
    )


    decision = resolver.resolve(
        result,
        consensus_confidence=0.8
    )


    assert decision["resolution"] == "ACCEPT_MAJORITY"

    assert decision["decision"] == "BUY"



def test_resolver_blocks_high_conflict():

    resolver = StrategyConflictResolver()


    result = StrategyConflictResult(

        conflict=True,

        conflict_level="HIGH",

        dominant_action=None,

        buy_support=2,

        sell_support=2
    )


    decision = resolver.resolve(
        result,
        consensus_confidence=0.8
    )


    assert decision["resolution"] == "HOLD"

    assert decision["decision"] is None



def test_resolver_rejects_low_confidence():

    resolver = StrategyConflictResolver()


    result = StrategyConflictResult(

        conflict=True,

        conflict_level="MEDIUM",

        dominant_action="BUY"
    )


    decision = resolver.resolve(
        result,
        consensus_confidence=0.4
    )


    assert decision["resolution"] == "REJECT"

    assert decision["decision"] is None