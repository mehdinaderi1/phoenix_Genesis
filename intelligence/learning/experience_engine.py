from intelligence.learning.experience_record import ExperienceRecord


class ExperienceEngine:

    def create_experience(
        self,
        symbol: str,
        strategy: str,
        regime: str,
        signal: str,
        confidence: float,
        profit_loss: float,
    ) -> ExperienceRecord:

        if profit_loss > 0:
            outcome = "SUCCESS"

            lesson = (
                f"{strategy} performed well "
                f"under {regime} regime"
            )

        else:
            outcome = "FAILURE"

            lesson = (
                f"{strategy} should be reviewed "
                f"under {regime} regime"
            )

        return ExperienceRecord(
            symbol=symbol,
            strategy=strategy,
            regime=regime,
            signal=signal,
            confidence=confidence,
            outcome=outcome,
            profit_loss=profit_loss,
            lesson=lesson,
        )