from intelligence.strategy_conflict import StrategyConflictResult


def test_strategy_conflict_result_contract():

    result = StrategyConflictResult(
        conflict=True,
        conflict_level="HIGH",
        dominant_action="BUY",
        buy_support=3,
        sell_support=2
    )


    data = result.to_dict()


    assert data["conflict"] is True

    assert data["conflict_level"] == "HIGH"

    assert data["dominant_action"] == "BUY"

    assert data["buy_support"] == 3

    assert data["sell_support"] == 2