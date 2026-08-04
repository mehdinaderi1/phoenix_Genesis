from dataclasses import dataclass

from intelligence.learning.self_improvement import ImprovementReport


@dataclass
class StrategyScore:
    strategy: str
    score: float
    samples: int = 0
    success_rate: float = 0


class StrategyOptimizer:

    def optimize(
        self,
        strategy: str,
        current_score: float,
        report: ImprovementReport,
    ) -> StrategyScore:

        score = current_score

        if report.win_rate >= 60:
            score += 5
       
        else:
            score -= 5

        score = max(0.0, min(100.0, score))

        return StrategyScore(
            strategy=strategy,
            score=score,
            samples=report.total_trades,
            success_rate=report.win_rate,
        )