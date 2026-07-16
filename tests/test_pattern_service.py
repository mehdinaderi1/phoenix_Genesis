from intelligence.pattern_service import PatternService
from intelligence.pattern_score import PatternScore



def test_pattern_service():


    patterns = [

        PatternScore(

            regime="TRENDING_BULLISH",

            action="PREPARE_LONG",

            samples=100,

            average_quality=90,

            reliability="HIGH",

            score=90,

            rank=1

        ),


        PatternScore(

            regime="RANGING",

            action="WAIT",

            samples=20,

            average_quality=70,

            reliability="MEDIUM",

            score=59,

            rank=2

        )

    ]



    service = PatternService()


    result = service.find_best_pattern(patterns)



    assert result.regime == "TRENDING_BULLISH"

    assert result.confidence == 100