from intelligence.pattern_ranker import PatternRanker
from intelligence.decision_pattern import DecisionPattern



def test_pattern_ranker():


    patterns = [

        DecisionPattern(

            regime="TRENDING_BULLISH",

            action="PREPARE_LONG",

            samples=100,

            average_quality=90

        ),


        DecisionPattern(

            regime="RANGING",

            action="WAIT",

            samples=5,

            average_quality=95

        )

    ]


    ranker = PatternRanker()


    result = ranker.rank(patterns)



    assert len(result) == 2


    assert result[0].regime == "TRENDING_BULLISH"

    assert result[0].rank == 1

    assert result[0].reliability == "HIGH"


    assert result[1].reliability == "LOW"