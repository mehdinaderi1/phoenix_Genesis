from intelligence.pattern_recognizer import PatternRecognizer
from intelligence.experience_record import ExperienceRecord



def test_pattern_recognition():

    recognizer = PatternRecognizer()


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
        )

    ]


    result = recognizer.recognize(
        experiences
    )


    assert result["pattern"] == (
        "bullish_buy_low"
    )

    assert result["samples"] == 2

    assert result["success_rate"] == 1.0

    assert result["avg_score"] == 7