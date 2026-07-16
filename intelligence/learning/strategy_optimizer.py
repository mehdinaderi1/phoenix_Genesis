from dataclasses import dataclass

from intelligence.learning.self_improvement import ImprovementReport


@dataclass
class StrategyScore:
    strategy: str
    score: float


class StrategyOptimizer:

    def optimize(
        self,
        strategy: str,
        current_score: float,
        report: ImprovementReport,
    ) -> StrategyScore:

        score = current_score

        if report.win_rate >= 70:
            score += 5

        elif report.win_rate >= 55:
            score += 1

        else:
            score -= 5

        score = max(0.0, min(100.0, score))

        return StrategyScore(
            strategy=strategy,
            score=score,
        )