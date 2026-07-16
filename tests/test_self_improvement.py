from intelligence.learning.self_improvement import SelfImprovement
from intelligence.performance_record import PerformanceRecord


def test_self_improvement():

    feedbacks = [
        PerformanceRecord(strategy="Trend",
                            profit_loss=2.5,
                            success=True),

        PerformanceRecord(strategy="Trend",
                            profit_loss=1.2,
                            success=True),

        PerformanceRecord(strategy="Trend",
                            profit_loss=-0.8,
                            success=False),
    ]

    report = SelfImprovement().analyze(feedbacks)

    assert report.total_trades == 3
    assert report.win_rate > 60
    assert report.average_profit > 1
    assert report.average_loss > 0