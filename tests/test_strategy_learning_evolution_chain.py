from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_learner import StrategyLearner
from intelligence.learning.strategy_evolution_engine import StrategyEvolutionEngine


def test_strategy_learning_evolution_chain():

    memory = StrategyMemory()

    learner = StrategyLearner(
        memory
    )

    patterns = [
        {
            "pattern": (
                "Bullish",
                "Buy",
                "Low"
            ),
            "samples": 10,
            "success_rate": 0.8,
            "avg_score": 85
        }
    ]


    learned = learner.learn(
        patterns
    )


    assert len(learned) == 1

    strategy = learned[0]


    assert strategy["score"] == 85
    assert strategy["success_rate"] == 0.8


    engine = StrategyEvolutionEngine()


    evaluation = engine.evaluate(
        strategy
    )


    assert evaluation["decision"] == "KEEP"


    evolved = engine.evolve(
        {
            "name": strategy["strategy"],
            "generation": 1
        },
        strategy["score"]
    )


    assert evolved["evolved"] is True
    assert evolved["parent"] == strategy["strategy"]
    assert evolved["generation"] == 2
    assert evolved["score"] == 95