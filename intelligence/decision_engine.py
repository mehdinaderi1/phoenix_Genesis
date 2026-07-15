from intelligence.decision import DecisionResult
from intelligence.decision_rules import DecisionRules


class DecisionEngine:


    def __init__(self):

        self.rules = DecisionRules()


    def decide(self, report):


        if self.rules.can_long(report):

            return DecisionResult(
                action="PREPARE_LONG",
                reason="Strong bullish signal with controlled risk",
                confidence=report.confidence
            )


        elif self.rules.can_short(report):

            return DecisionResult(
                action="PREPARE_SHORT",
                reason="Bearish market conditions detected",
                confidence=report.confidence
            )


        else:

            return DecisionResult(
                action="WAIT",
                reason="Market conditions require monitoring",
                confidence=report.confidence
            )