from intelligence.decision import DecisionResult


class DecisionEngine:


    def decide(self, report):

        if (
            report.signal == "BUY"
            and report.risk == "LOW"
            and report.confidence >= 80
        ):

            return DecisionResult(
                action="PREPARE_LONG",
                reason="Strong bullish signal with controlled risk",
                confidence=report.confidence
            )


        elif report.signal == "SELL":

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