from dataclasses import dataclass

from intelligence.performance_record import PerformanceRecord


@dataclass
class ConfidenceCalibrationResult:
    original_confidence: float
    calibrated_confidence: float
    adjustment: float


class ConfidenceCalibrator:
    """
    Adjusts future confidence based on historical trading performance.

    The adjustment is intentionally conservative to avoid
    overreacting to a small number of trades.
    """

    def calibrate(
        self,
        confidence: float,
        feedbacks: list[PerformanceRecord],
    ) -> ConfidenceCalibrationResult:

        if not feedbacks:
            return ConfidenceCalibrationResult(
                original_confidence=confidence,
                calibrated_confidence=confidence,
                adjustment=0.0,
            )

        wins = sum(1 for feedback in feedbacks if feedback.success)

        actual_success = wins / len(feedbacks) * 100

        difference = actual_success - confidence

        # Conservative adjustment (20% of the gap)
        adjustment = difference * 0.20

        calibrated = confidence + adjustment

        calibrated = max(0.0, min(100.0, calibrated))

        return ConfidenceCalibrationResult(
            original_confidence=confidence,
            calibrated_confidence=calibrated,
            adjustment=adjustment,
        )