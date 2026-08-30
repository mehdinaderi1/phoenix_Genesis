from intelligence.pattern_intelligence import PatternIntelligence
from intelligence.strategy_learner import StrategyLearner
from intelligence.strategy_memory import StrategyMemory
from intelligence.memory.experience_memory import ExperienceMemory
from intelligence.experience_record import ExperienceRecord


def make_experience(
    strategy,
    success,
    score
):
    return ExperienceRecord(
        regime="TREND",
        signal="BUY",
        risk="LOW",
        success=success,
        score=score,
        decision="PREPARE_LONG",
        strategy=strategy,
        confidence=80,
        trace={},
        champion_strategy={
            "name": strategy
        }
    )


def test_pattern_to_multi_strategy_learning_flow():

    experience_memory = ExperienceMemory()

    for _ in range(8):

        experience_memory.save_experience(
            make_experience(
                "strategy_A",
                True,
                80
            )
        )

    for _ in range(2):

        experience_memory.save_experience(
            make_experience(
                "strategy_A",
                False,
                40
            )
        )

    for _ in range(7):

        experience_memory.save_experience(
            make_experience(
                "strategy_B",
                True,
                70
            )
        )

    for _ in range(3):

        experience_memory.save_experience(
            make_experience(
                "strategy_B",
                False,
                40
            )
        )

    pattern_intelligence = PatternIntelligence()

    patterns = pattern_intelligence.analyze(
        experience_memory.get_experiences()
    )

    assert len(patterns) == 1

    pattern = patterns[0]

    assert "strategies" in pattern

    assert set(
        pattern["strategies"].keys()
    ) == {
        "strategy_A",
        "strategy_B"
    }

    strategy_memory = StrategyMemory()

    learner = StrategyLearner(
        strategy_memory= strategy_memory
    )

    learned = learner.learn(
        patterns
    )

    assert len(learned) == 2

    assert strategy_memory.count() == 2

    names = {
        strategy["strategy"]
        for strategy in learned
    }

    assert names == {
        "strategy_A",
        "strategy_B"
    }
