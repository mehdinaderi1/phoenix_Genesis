class DecisionRules:


    def can_long(self, report):

        return (
            report.signal == "BUY"
            and report.risk == "LOW"
            and report.confidence >= 80
        )


    def can_short(self, report):

        return (
            report.signal == "SELL"
            and report.confidence >= 70
        )