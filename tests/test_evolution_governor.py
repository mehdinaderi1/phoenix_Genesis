from intelligence.evolution.evolution_governor import (
    EvolutionGovernor
)



def test_governor_approves_healthy_evolution():


    governor = EvolutionGovernor()


    awareness = {

        "maturity":
            "ADVANCED",

        "health":
            0.95,

        "trend":
            "IMPROVING"

    }


    result = governor.decide(
        awareness
    )


    assert (
        result["decision"]
        ==
        "APPROVE"
    )


    assert (
        result["reason"]
        ==
        "healthy evolution state"
    )



def test_governor_retires_bad_evolution():


    governor = EvolutionGovernor()


    awareness = {

        "maturity":
            "EARLY",

        "health":
            0.2,

        "trend":
            "STABLE"

    }


    result = governor.decide(
        awareness
    )


    assert (
        result["decision"]
        ==
        "RETIRE"
    )



def test_governor_holds_uncertain_case():


    governor = EvolutionGovernor()


    awareness = {

        "maturity":
            "DEVELOPING",

        "health":
            0.6,

        "trend":
            "STABLE"

    }


    result = governor.decide(
        awareness
    )


    assert (
        result["decision"]
        ==
        "HOLD"
    )