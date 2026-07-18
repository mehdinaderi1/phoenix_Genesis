from dataclasses import dataclass

from intelligence.performance_record import PerformanceRecord


@dataclass
class ImprovementReport:
    total_trades: int
    win_rate: float
    average_profit: float
    average_loss: float
    recommendation: str


class SelfImprovement:

    def analyze(self, feedbacks: list[PerformanceRecord]) -> ImprovementReport:

        if not feedbacks:
            return ImprovementReport(
                total_trades=0,
                win_rate=0.0,
                average_profit=0.0,
                average_loss=0.0,
                recommendation="No Data",
            )

        wins = [f for f in feedbacks if f.profit_loss > 0]
        losses = [f for f in feedbacks if f.profit_loss <= 0]

        total = len(feedbacks)

        win_rate = len(wins) / total * 100

        avg_profit = (
            sum(f.profit_loss for f in wins) / len(wins)
            if wins
            else 0.0
        )

        avg_loss = (
            abs(sum(f.profit_loss for f in losses) / len(losses))
            if losses
            else 0.0
        )

        if win_rate >= 70:
            recommendation = "Increase Confidence"

        elif win_rate >= 55:
            recommendation = "Keep Strategy"

        else:
            recommendation = "Review Strategy"

        return ImprovementReport(
            total_trades=total,
            win_rate=win_rate,
            average_profit=avg_profit,
            average_loss=avg_loss,
            recommendation=recommendation,
        )