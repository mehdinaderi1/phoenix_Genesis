from intelligence.experience_confidence import ExperienceConfidence


def test_experience_confidence_bonus_from_history():

    engine = ExperienceConfidence()

    experience_context = {

        "total_experiences": 10,

        "successful": 8

    }


    bonus = engine.calculate(
        experience_context
    )


    assert bonus > 0


def test_experience_confidence_bonus_for_bad_history():

    engine = ExperienceConfidence()

    experience_context = {

        "total_experiences": 10,

        "successful": 2

    }


    bonus = engine.calculate(
        experience_context
    )


    assert bonus < 0