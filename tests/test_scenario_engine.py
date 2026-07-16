from intelligence.scenario_engine import ScenarioEngine


def test_scenario_generation():

    engine = ScenarioEngine()


    result = engine.generate(

        "TRENDING_BULLISH",

        85,

        "LOW"

    )


    assert result is not None

    assert len(result) == 3

    assert result[0]["name"] == "BULLISH_CONTINUATION"

    assert result[0]["probability"] > 0