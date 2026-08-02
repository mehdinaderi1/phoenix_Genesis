from intelligence.evolution.self_evolution_orchestrator import (
    SelfEvolutionOrchestrator
)



class DummyAwareness:


    def evaluate(
        self,
        strategy
    ):

        return {

            "generation": 2,

            "maturity":
                "ADVANCED",

            "health":
                0.95,

            "trend":
                "IMPROVING"

        }



class DummyGovernor:


    def decide(
        self,
        awareness
    ):

        return {

            "decision":
                "APPROVE"

        }



class DummyPolicy:


    def evaluate(
        self,
        data
    ):

        return {

            "allowed":
                True

        }



def test_orchestrator_allows_valid_evolution():


    orchestrator = SelfEvolutionOrchestrator(

        DummyAwareness(),

        DummyGovernor(),

        DummyPolicy()

    )


    result = orchestrator.evaluate(

        "momentum_strategy_v3"

    )


    assert (
        result["allowed"]
        is True
    )


    assert (
        result["governor"]["decision"]
        ==
        "APPROVE"
    )


    assert (
        result["policy"]["allowed"]
        is True
    )