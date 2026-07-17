from intelligence.experience_confidence import ExperienceConfidence



def test_experience_confidence_positive():

    engine = ExperienceConfidence()

    context = {

        "total_experiences": 10,

        "successful": 8

    }


    result = engine.calculate(context)


    assert result > 0



def test_experience_confidence_negative():

    engine = ExperienceConfidence()

    context = {

        "total_experiences": 10,

        "successful": 2

    }


    result = engine.calculate(context)


    assert result < 0



def test_experience_confidence_limit():

    engine = ExperienceConfidence()

    context = {

        "total_experiences": 100,

        "successful": 100

    }


    result = engine.calculate(context)


    assert result <= 10



def test_experience_confidence_from_strategy():

    engine = ExperienceConfidence()


    strategy = {

        "strategy": "bullish_buy_low",

        "success_rate": 0.8

    }


    result = engine.calculate_from_strategy(
        strategy
    )


    assert result == 6