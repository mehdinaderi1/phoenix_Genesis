from intelligence.evolution.evolution_execution import (
    EvolutionExecution,
)


class DummyController:


    def run(
        self,
        strategy,
        score
    ):

        return {
            "action": "KEEP",
            "strategy": strategy,
            "score": score
        }



def test_evolution_execution():

    execution = EvolutionExecution(
        DummyController()
    )


    result = execution.execute(
        "trend_v2",
        90
    )


    assert result["executed"] is True

    assert (
        result["result"]["action"]
        == "KEEP"
    )