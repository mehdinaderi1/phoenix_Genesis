from intelligence.pattern_cluster import PatternCluster
from intelligence.experience_record import ExperienceRecord



def test_pattern_cluster():


    cluster = PatternCluster()


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
            7
        ),

        ExperienceRecord(
            "bearish",
            "sell",
            "high",
            False,
            3
        )

    ]


    result = cluster.cluster(
        experiences
    )


    assert len(result) == 2


    assert len(
        result["bullish_buy_low"]
    ) == 2


    assert len(
        result["bearish_sell_high"]
    ) == 1