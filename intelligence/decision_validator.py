import os


class DecisionValidator:

    USE_RELAXED_RULES = (
        os.getenv("PHOENIX_RELAXED_RULES", "0").strip() == "1"
    )

    MIN_CONFIDENCE = 30 if USE_RELAXED_RULES else 70

    def validate(self, decision):

        if decision.action == "WAIT":
            return False

        if decision.confidence < self.MIN_CONFIDENCE:
            return False

        return True