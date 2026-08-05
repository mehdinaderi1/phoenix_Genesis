from intelligence.strategy_validator import StrategyValidator



def test_strategy_validator_accepts_strong_active_strategy():

    validator = StrategyValidator()


    strategy = {

        "name": "trend_following",

        "status": "ACTIVE",

        "score": 90,

        "success_rate": 0.85,

        "samples": 50

    }


    result = validator.validate(
        strategy
    )


    assert result["valid"] is True

    assert result["confidence"] >= 70



def test_strategy_validator_rejects_inactive_strategy():

    validator = StrategyValidator()


    strategy = {

        "name": "old_strategy",

        "status": "RETIRED",

        "score": 95,

        "success_rate": 0.90,

        "samples": 100

    }


    result = validator.validate(
        strategy
    )


    assert result["valid"] is False

    assert result["reason"] == "NOT_ACTIVE"



def test_strategy_validator_rejects_low_quality_strategy():

    validator = StrategyValidator()


    strategy = {

        "name": "weak_strategy",

        "status": "ACTIVE",

        "score": 40,

        "success_rate": 0.30,

        "samples": 5

    }


    result = validator.validate(
        strategy
    )


    assert result["valid"] is False