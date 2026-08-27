from intelligence.experience_record import ExperienceRecord
from intelligence.pattern_intelligence import PatternIntelligence
from intelligence.strategy_learner import StrategyLearner
from intelligence.strategy_memory import StrategyMemory


def test_pattern_learning_preserves_champion_strategy_identity():

    experiences = [

        ExperienceRecord(
            "bullish",
            "buy",
            "low",
            True,
            85,
            strategy="trend_following",
            champion_strategy={
                "name": "trend_following"
            }
        )

        for _ in range(5)

    ]


    intelligence = PatternIntelligence()


    patterns = intelligence.analyze(
        experiences
    )


    assert patterns

    assert patterns[0]["strategy"] == (
        "trend_following"
    )


    memory = StrategyMemory()


    learner = StrategyLearner(
        memory
    )


    learned = learner.learn(
        patterns
    )


    assert learned

    assert learned[0]["strategy"] == (
        "trend_following"
    )