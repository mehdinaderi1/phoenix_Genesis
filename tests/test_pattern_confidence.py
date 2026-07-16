from intelligence.pattern_confidence_analyzer import PatternConfidenceAnalyzer
from intelligence.pattern_score import PatternScore



def test_pattern_confidence():


    patterns = [

        PatternScore(

            regime="TRENDING_BULLISH",

            action="PREPARE_LONG",

            samples=100,

            average_quality=90,

            reliability="HIGH",

            score=90,

            rank=1

        )

    ]


    analyzer = PatternConfidenceAnalyzer()


    result = analyzer.analyze(patterns)



    assert len(result) == 1


    assert result[0].confidence == 100


    assert result[0].reliability == "HIGH"

    assert result[0].samples == 100