from intelligence.evolution.evolution_policy import (
    EvolutionPolicy
)



def test_policy_allows_valid_evolution():


    policy = EvolutionPolicy()


    evolution = {

        "generation":
            2,

        "confidence":
            90,

        "decision":
            "APPROVE"

    }


    result = policy.evaluate(
        evolution
    )


    assert (
        result["allowed"]
        is True
    )


    assert (
        result["reason"]
        ==
        "policy satisfied"
    )



def test_policy_blocks_low_confidence():


    policy = EvolutionPolicy()


    evolution = {

        "generation":
            2,

        "confidence":
            40,

        "decision":
            "APPROVE"

    }


    result = policy.evaluate(
        evolution
    )


    assert (
        result["allowed"]
        is False
    )



def test_policy_blocks_generation_overflow():


    policy = EvolutionPolicy(
        max_generation=3
    )


    evolution = {

        "generation":
            5,

        "confidence":
            90,

        "decision":
            "APPROVE"

    }


    result = policy.evaluate(
        evolution
    )


    assert (
        result["allowed"]
        is False
    )