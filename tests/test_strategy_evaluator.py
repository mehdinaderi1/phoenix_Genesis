from intelligence.strategy_evaluator import StrategyEvaluator



def test_strategy_evaluator_accepts_good_strategy():

    evaluator = StrategyEvaluator()


    strategy = {

        "samples": 50,

        "success_rate": 0.8

    }


    result = evaluator.evaluate(
        strategy
    )


    assert result["accepted"] is True



def test_strategy_evaluator_rejects_low_samples():

    evaluator = StrategyEvaluator()


    strategy = {

        "samples": 2,

        "success_rate": 0.9

    }


    result = evaluator.evaluate(
        strategy
    )


    assert result["accepted"] is False



def test_strategy_evaluator_rejects_low_success():

    evaluator = StrategyEvaluator()


    strategy = {

        "samples": 50,

        "success_rate": 0.3

    }


    result = evaluator.evaluate(
        strategy
    )


    assert result["accepted"] is False