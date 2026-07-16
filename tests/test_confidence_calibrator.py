from intelligence.learning.confidence_calibrator import (
    ConfidenceCalibrator,
)
from intelligence.performance_record import (
    PerformanceRecord,
)


def test_confidence_should_increase():

    feedbacks = [
        PerformanceRecord(
            strategy="Trend",
            profit_loss=1,
            success=True,
        ),
        PerformanceRecord(
            strategy="Trend",
            profit_loss=2,
            success=True,
        ),
        PerformanceRecord(
            strategy="Trend",
            profit_loss=1,
            success=True,
        ),
        PerformanceRecord(
            strategy="Trend",
            profit_loss=-1,
            success=False,
        ),
    ]

    result = ConfidenceCalibrator().calibrate(60, feedbacks)

    assert result.calibrated_confidence > 60


def test_confidence_should_decrease():

    feedbacks = [
        PerformanceRecord(
            strategy="Trend",
            profit_loss=-1,
            success=False,
        ),
        PerformanceRecord(
            strategy="Trend",
            profit_loss=-2,
            success=False,
        ),
        PerformanceRecord(
            strategy="Trend",
            profit_loss=1,
            success=True,
        ),
        PerformanceRecord(
            strategy="Trend",
            profit_loss=-1,
            success=False,
        ),
    ]

    result = ConfidenceCalibrator().calibrate(80, feedbacks)

    assert result.calibrated_confidence < 80


def test_confidence_without_history():

    result = ConfidenceCalibrator().calibrate(75, [])

    assert result.calibrated_confidence == 75


def test_confidence_never_above_100():

    feedbacks = [
        PerformanceRecord(
            strategy="Trend",
            profit_loss=1,
            success=True,
        )
        for _ in range(50)
    ]

    result = ConfidenceCalibrator().calibrate(99, feedbacks)

    assert result.calibrated_confidence == 99.2


def test_confidence_never_below_zero():

    feedbacks = [
        PerformanceRecord(
            strategy="Trend",
            profit_loss=-1,
            success=False,
        )
        for _ in range(50)
    ]

    result = ConfidenceCalibrator().calibrate(2, feedbacks)

    assert result.calibrated_confidence >= 0