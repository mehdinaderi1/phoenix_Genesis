from intelligence.memory.experience_matcher import (
    ExperienceMatcher
)


class MockExperience:

    def __init__(
        self,
        regime,
        signal,
        risk,
        success,
        score
    ):

        self.regime = regime
        self.signal = signal
        self.risk = risk
        self.success = success
        self.score = score



class MockContext:

    def __init__(
        self,
        regime,
        signal,
        risk
    ):

        self.regime = regime
        self.signal = signal
        self.risk = risk



def test_experience_match_found():

    experiences = [

        MockExperience(
            regime="TREND",
            signal="BUY",
            risk="LOW",
            success=True,
            score=90
        )

    ]


    context = MockContext(

        regime="TREND",
        signal="BUY",
        risk="LOW"

    )


    matcher = ExperienceMatcher()


    result = matcher.match(
        context,
        experiences
    )


    assert result.similar_cases == 1

    assert result.success_rate == 1

    assert result.average_score == 90



def test_no_similar_experience():

    experiences = [

        MockExperience(
            regime="RANGE",
            signal="SELL",
            risk="HIGH",
            success=False,
            score=20
        )

    ]


    context = MockContext(

        regime="TREND",
        signal="BUY",
        risk="LOW"

    )


    matcher = ExperienceMatcher()


    result = matcher.match(
        context,
        experiences
    )


    assert result.similar_cases == 0

    assert result.success_rate == 0

    assert result.average_score == 0



def test_partial_similarity():

    experiences = [

        MockExperience(
            regime="TREND",
            signal="BUY",
            risk="HIGH",
            success=True,
            score=80
        ),

        MockExperience(
            regime="RANGE",
            signal="SELL",
            risk="LOW",
            success=False,
            score=30
        )

    ]


    context = MockContext(

        regime="TREND",
        signal="BUY",
        risk="LOW"

    )


    matcher = ExperienceMatcher()


    result = matcher.match(
        context,
        experiences
    )


    assert result.similar_cases == 1

    assert result.success_rate == 1

    assert result.average_score == 80