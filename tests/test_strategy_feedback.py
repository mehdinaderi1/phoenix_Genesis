from intelligence.strategy_feedback import StrategyFeedback


def test_strategy_feedback_creates_record():

    feedback = {

        "result": "SUCCESS",

        "score": 100

    }


    record = StrategyFeedback().create_record(
        "Trend",
        feedback
    )


    assert record.strategy == "Trend"

    assert record.success is True

    assert record.profit_loss == 1