from intelligence.experience_confidence import ExperienceConfidence


def test_experience_bonus_affects_confidence():

    engine = ExperienceConfidence()

    context = {
        "total_experiences": 10,
        "successful": 9
    }

    bonus = engine.calculate(context)

    confidence = 60 + bonus

    assert confidence > 60