from intelligence.pattern_intelligence import PatternIntelligence
from intelligence.experience_record import ExperienceRecord



def test_pattern_intelligence():


    engine = PatternIntelligence()


    experiences = [

        ExperienceRecord(
            "bullish",
            "buy",
            "low",
            True,
            8
        ),

        ExperienceRecord(
            "bullish",
            "buy",
            "low",
            True,
            6
        ),

        ExperienceRecord(
            "bearish",
            "sell",
            "high",
            False,
            3
        )

    ]


    result = engine.analyze(
        experiences
    )


    assert len(result) == 2


    bullish = result[0]


    assert "pattern" in bullish

    assert "samples" in bullish

    assert "success_rate" in bullish