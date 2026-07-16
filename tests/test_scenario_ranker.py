from intelligence.scenario_ranker import ScenarioRanker



def test_scenario_ranker():


    ranker = ScenarioRanker()


    scenarios = [

        {
            "name": "BULLISH_CONTINUATION",
            "probability": 80,
            "reason": "Strong trend"
        },

        {
            "name": "SIDEWAYS",
            "probability": 30,
            "reason": "Consolidation"
        },

        {
            "name": "BEARISH_REVERSAL",
            "probability": 10,
            "reason": "Risk"
        }

    ]


    result = ranker.rank(
        scenarios
    )


    assert result is not None

    assert result["primary_scenario"] == "BULLISH_CONTINUATION"

    assert result["probability"] == 80