class DecisionRules:


    def strategy_is_valid(self, report):

        strategy = getattr(
            report,
            "champion_strategy",
            None
        )


        if strategy is None:
            return True


        return strategy.get("status") == "ACTIVE"



    def can_long(self, report):

        return (
            self.strategy_is_valid(report)
            and report.signal == "BUY"
            and report.risk == "LOW"
            and report.confidence >= 80
        )



    def can_short(self, report):

        return (
            self.strategy_is_valid(report)
            and report.signal == "SELL"
            and report.confidence >= 70
        )