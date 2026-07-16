from intelligence.learning.strategy_optimizer import StrategyOptimizer
from intelligence.learning.self_improvement import ImprovementReport


def test_strategy_score_increase():

    report = ImprovementReport(
        total_trades=20,
        win_rate=80,
        average_profit=2.5,
        average_loss=1.0,
        recommendation="Increase Confidence",
    )

    result = StrategyOptimizer().optimize(
        strategy="Trend",
        current_score=70,
        report=report,
    )

    assert result.score == 75


def test_strategy_score_decrease():

    report = ImprovementReport(
        total_trades=20,
        win_rate=40,
        average_profit=1,
        average_loss=2,
        recommendation="Review Strategy",
    )

    result = StrategyOptimizer().optimize(
        strategy="Breakout",
        current_score=60,
        report=report,
    )

    assert result.score == 55


def test_score_limits():

    report = ImprovementReport(
        total_trades=20,
        win_rate=95,
        average_profit=5,
        average_loss=1,
        recommendation="Increase Confidence",
    )

    result = StrategyOptimizer().optimize(
        strategy="Trend",
        current_score=99,
        report=report,
    )

    assert result.score == 100