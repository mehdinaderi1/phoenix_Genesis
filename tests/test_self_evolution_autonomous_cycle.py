from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine
)

from intelligence.evolution.evolution_memory import (
    EvolutionMemory
)

from intelligence.evolution.evolution_governor import (
    EvolutionGovernor
)

from intelligence.evolution.evolution_policy import (
    EvolutionPolicy
)


def test_self_evolution_autonomous_cycle():


    memory = EvolutionMemory()

    engine = StrategyEvolutionEngine()

    governor = EvolutionGovernor()

    policy = EvolutionPolicy()



    # Generation 1

    strategy = {

        "name":
            "momentum_strategy",

        "generation":
            1,

        "score":
            60,

        "success_rate":
            0.6

    }



    first = engine.evolve(

        strategy,

        80

    )


    assert (
        first["evolved"]
        is True
    )


    assert (
        first["generation"]
        ==
        2
    )



    # Feedback from v2

    feedback_score = 90



    memory.store(

        type(
            "Record",
            (),
            {

                "parent":
                    strategy["name"],

                "child":
                    first["strategy"],

                "generation":
                    first["generation"],

                "score_after":
                    feedback_score

            }

        )()

    )



    assert (
        memory.count()
        ==
        1
    )



    # Self awareness simulation

    awareness = {

        "generation":
            2,

        "maturity":
            "ADVANCED",

        "health":
            0.95,

        "trend":
            "IMPROVING",

        "confidence":
            90

    }



    governor_result = governor.decide(

        awareness

    )


    assert (
        governor_result["decision"]
        ==
        "APPROVE"
    )



    policy_result = policy.evaluate(

        {

            **awareness,

            "decision":
                governor_result["decision"]

        }

    )


    assert (
        policy_result["allowed"]
        is True
    )



    # Generation 2 -> 3

    second_strategy = {

        "name":
            first["strategy"],

        "generation":
            first["generation"],

        "score":
            feedback_score

    }



    second = engine.evolve(

        second_strategy,

        90

    )


    assert (
        second["evolved"]
        is True
    )


    assert (
        second["generation"]
        >
        first["generation"]
    )


    memory.store(

        type(
            "Record",
            (),
            {

                "parent":
                    second_strategy["name"],

                "child":
                    second["strategy"],

                "generation":
                    second["generation"],

                "score_after":
                    second["score"]

            }

        )()

    )


    assert (
        memory.count()
        ==
        2
    )