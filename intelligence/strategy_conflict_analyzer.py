from intelligence.strategy_conflict import StrategyConflictResult


class StrategyConflictAnalyzer:
    """
    Analyzes disagreement between multiple strategies.
    """



    def analyze(
        self,
        strategies
    ):

        if not strategies:

            return StrategyConflictResult(

                conflict=False,

                conflict_level="LOW"
            )



        buy_support = 0

        sell_support = 0

        conflicting_strategies = []



        for strategy in strategies:

            action = strategy.get(
                "action"
            )


            if action == "BUY":

                buy_support += 1


            elif action == "SELL":

                sell_support += 1


            else:

                continue



        total = (
            buy_support
            +
            sell_support
        )



        if total == 0:

            return StrategyConflictResult(

                conflict=False,

                conflict_level="LOW",

                total_strategies=len(strategies)
            )



        dominant_action = None


        if buy_support > sell_support:

            dominant_action = "BUY"


        elif sell_support > buy_support:

            dominant_action = "SELL"



        conflict = (
            buy_support > 0
            and
            sell_support > 0
        )



        if not conflict:

            level = "LOW"

            penalty = 0.0



        elif buy_support == sell_support:

            level = "HIGH"

            penalty = 0.25



        else:

            level = "MEDIUM"

            penalty = 0.10



        for strategy in strategies:

            action = strategy.get(
                "action"
            )


            if (
                action
                and
                action != dominant_action
            ):

                conflicting_strategies.append(
                    strategy
                )



        return StrategyConflictResult(

            conflict=conflict,

            conflict_level=level,

            dominant_action=dominant_action,

            buy_support=buy_support,

            sell_support=sell_support,

            total_strategies=total,

            confidence_penalty=penalty,

            conflicting_strategies=
                conflicting_strategies,

            explanation={

                "buy_support":
                    buy_support,

                "sell_support":
                    sell_support,

                "dominant_action":
                    dominant_action
            }
        )