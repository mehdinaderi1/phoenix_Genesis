from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController,
)


class DummyStrategyEngine:


    def evolve(
        self,
        strategy,
        score
    ):

        if score < 70:

            return {

                "evolved": False,

                "strategy": strategy,

                "score": score

            }


        return {

            "evolved": True,

            "strategy": strategy["name"] + "_v2",

            "score": score + 10

        }



class DummyAnalytics:

    pass



class DummyDecision:


    def decide(
        self,
        new_score,
        old_score
    ):

        if new_score < old_score:

            return {
                "decision": "ROLLBACK"
            }


        return {
            "decision": "KEEP"
        }



class DummyRollback:

    pass



def create_controller():

    return SelfEvolutionController(

        evolution_engine=DummyStrategyEngine(),

        analytics=DummyAnalytics(),

        decision=DummyDecision(),

        rollback=DummyRollback()

    )



def test_strong_strategy_can_evolve():

    controller = create_controller()


    strategy = {

        "name": "trend_v1",

        "score": 90,

        "success_rate": 0.85

    }


    result = controller.run(
        strategy,
        strategy["score"]
    )


    assert result is not None



def test_weak_strategy_blocked():

    controller = create_controller()


    strategy = {

        "name": "trend_bad",

        "score": 40,

        "success_rate": 0.2

    }


    result = controller.run(
        strategy,
        strategy["score"]
    )


    assert result is not None