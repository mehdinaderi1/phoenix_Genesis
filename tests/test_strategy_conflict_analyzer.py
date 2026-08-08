from intelligence.strategy_conflict_analyzer import (
    StrategyConflictAnalyzer
)



def test_strategy_conflict_no_conflict():

    analyzer = StrategyConflictAnalyzer()


    result = analyzer.analyze(
        [
            {
                "name": "momentum",
                "action": "BUY"
            },
            {
                "name": "trend",
                "action": "BUY"
            }
        ]
    )


    assert result.conflict is False

    assert result.dominant_action == "BUY"

    assert result.conflict_level == "LOW"



def test_strategy_conflict_majority_conflict():

    analyzer = StrategyConflictAnalyzer()


    result = analyzer.analyze(
        [
            {
                "name": "momentum",
                "action": "BUY"
            },
            {
                "name": "trend",
                "action": "BUY"
            },
            {
                "name": "reversal",
                "action": "SELL"
            }
        ]
    )


    assert result.conflict is True

    assert result.dominant_action == "BUY"

    assert result.conflict_level == "MEDIUM"

    assert result.confidence_penalty == 0.10



def test_strategy_conflict_equal_vote():

    analyzer = StrategyConflictAnalyzer()


    result = analyzer.analyze(
        [
            {
                "name": "momentum",
                "action": "BUY"
            },
            {
                "name": "reversal",
                "action": "SELL"
            }
        ]
    )


    assert result.conflict is True

    assert result.conflict_level == "HIGH"

    assert result.dominant_action is None

    assert result.confidence_penalty == 0.25