import os


class DecisionValidator:

    USE_RELAXED_RULES = (
        os.getenv("PHOENIX_RELAXED_RULES", "0").strip() == "1"
    )

    MIN_CONFIDENCE = float(os.getenv(
        "PHOENIX_DECISION_MIN_CONFIDENCE",
        "30" if USE_RELAXED_RULES else "70"
    ))

    SKIP_VALIDATION = (
        os.getenv("PHOENIX_SKIP_DECISION_VALIDATION", "0").strip() == "1"
    )

    def validate(self, decision):

        if self.SKIP_VALIDATION:
            return True

        if decision.action == "WAIT":
            return False

        if decision.confidence < self.MIN_CONFIDENCE:
            return False

        return True