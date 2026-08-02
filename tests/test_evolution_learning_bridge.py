from intelligence.evolution.evolution_learning_bridge import (
    EvolutionLearningBridge
)



class MockAnalytics:

    def average_improvement(self):

        return 20



def test_learning_bridge_generates_learning_signal():

    bridge = EvolutionLearningBridge(
        MockAnalytics()
    )


    result = bridge.evaluate(

        "strategy_v1",

        "strategy_v2",

        {
            "score": 40,
            "success_rate": 0.3
        }

    )


    assert result["learning"] is True

    assert (
        result["confidence"]
        ==
        0.90
    )


    assert (
        result["reason"]
        ==
        "Low success rate"
    )



def test_learning_bridge_detects_stable_strategy():

    bridge = EvolutionLearningBridge(
        MockAnalytics()
    )


    result = bridge.evaluate(

        "strategy_v1",

        "strategy_v2",

        {
            "score": 95,
            "success_rate": 0.95
        }

    )


    assert result["learning"] is False


    assert (
        result["reason"]
        ==
        "Stable strategy"
    )