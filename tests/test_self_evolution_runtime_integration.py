from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController
)

from intelligence.evolution.self_evolution_orchestrator import (
    SelfEvolutionOrchestrator
)



class DummyEngine:

    def evolve(
        self,
        strategy,
        score
    ):

        return {

            "strategy":
                "strategy_v2",

            "score":
                90,

            "generation":
                2,

            "evolved":
                True

        }



class DummyAnalytics:
    pass



class DummyDecision:

    def decide(
        self,
        score,
        parent
    ):

        return {

            "decision":
                "KEEP"

        }



class DummyRollback:
    pass



class AllowAwareness:


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



class AllowGovernor:


    def decide(
        self,
        awareness
    ):

        return {

            "decision":
                "APPROVE"

        }



class AllowPolicy:


    def evaluate(
        self,
        data
    ):

        return {

            "allowed":
                True

        }



def test_runtime_uses_orchestrator():


    orchestrator = SelfEvolutionOrchestrator(

        AllowAwareness(),

        AllowGovernor(),

        AllowPolicy()

    )


    controller = SelfEvolutionController(

        evolution_engine=
            DummyEngine(),

        analytics=
            DummyAnalytics(),

        decision=
            DummyDecision(),

        rollback=
            DummyRollback(),

        orchestrator=
            orchestrator

    )


    result = controller.run(

        {
            "name":
                "strategy"
        },

        80

    )


    assert (
        result["action"]
        ==
        "KEEP"
    )


    assert (
        result["orchestrator"]["allowed"]
        is True
    )