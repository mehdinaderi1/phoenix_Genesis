from intelligence.evolution.evolution_confidence import (
    EvolutionConfidence
)



def test_evolution_confidence_increases_after_success():

    calculator = EvolutionConfidence()


    old_strategy = {

        "name": "momentum_strategy",

        "score": 55,

        "success_rate": 0.5,

        "generation": 1

    }


    new_strategy = {

        "name": "momentum_strategy_v2",

        "score": 85,

        "success_rate": 0.85,

        "generation": 2

    }


    before = calculator.calculate(
        old_strategy
    )


    after = calculator.calculate(
        new_strategy
    )


    assert (
        after["confidence"]
        >
        before["confidence"]
    )


    assert (
        after["confidence"]
        >=
        80
    )


    assert (
        "successful evolution history"
        in
        after["reason"]
    )



def test_evolution_confidence_clamped():

    calculator = EvolutionConfidence()


    bad_strategy = {

        "score": 0,

        "success_rate": 0,

        "generation": 1

    }


    result = calculator.calculate(
        bad_strategy
    )


    assert (
        result["confidence"]
        >=
        0
    )


    assert (
        result["confidence"]
        <=
        100
    )



def test_unknown_strategy_returns_default_confidence():

    calculator = EvolutionConfidence()


    result = calculator.calculate(
        None
    )


    assert (
        result["confidence"]
        ==
        50
    )