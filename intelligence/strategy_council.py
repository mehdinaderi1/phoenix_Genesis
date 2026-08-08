from intelligence.strategy_council_result import (
    StrategyCouncilResult
)


class StrategyCouncil:
    """
    Evaluates multiple strategies and produces a weighted consensus decision.
    """

    def evaluate(
        self,
        strategies
    ):

        # v4.6 StrategyRankingResult support

        if hasattr(
            strategies,
            "ranked_strategies"
        ):
            strategies = (
                strategies.ranked_strategies
            )


        if not strategies:
            return None


        support = {}

        weighted_support = {}

        strategy_weights = {}

        strategy_votes = []

        supporting_names = []

        conflicting_names = []

        top_strategy = None

        top_score = -1


        for strategy in strategies:


            if hasattr(
                strategy,
                "strategy_record"
            ):

                data = (
                    strategy.strategy_record
                )

                score = getattr(
                    strategy,
                    "final_score",
                    0
                )

                name = getattr(
                    strategy,
                    "strategy_name",
                    None
                )


            else:

                data = strategy

                score = data.get(
                    "score",
                    0
                )

                name = data.get(
                    "name"
                )


            action = data.get(
                "action"
            )


            if not action:
                continue


            confidence = data.get(
                "confidence",
                0
            )

            strategy_votes.append(
            {
                "strategy": name,
                "action": action,
                "confidence": confidence,
                "score": score
        }
    )


            weight = (
                confidence *
                score
            )


            weighted_support[action] = (
                weighted_support.get(
                    action,
                    0
                )
                +
                weight
            )


            support[action] = (
                support.get(
                    action,
                    0
                )
                +
                1
            )


            strategy_weights[action] = (
                strategy_weights.get(
                    action,
                    0
                )
                +
                score
            )


            if score > top_score:

                top_score = score

                top_strategy = name



        if not support:
            return None



        decision = max(
            support,
            key=support.get
        )


        supporting = support.get(
            decision,
            0
        )


        opposing = (
            len(strategies)
            -
            supporting
        )


        total_weight = sum(
            weighted_support.values()
        )


        confidence = (

            weighted_support.get(
                decision,
                0
            )
            /
            total_weight

            if total_weight

            else 0

        )

        for vote in strategy_votes:

            if vote["action"] == decision:

                supporting_names.append(
                    vote["strategy"]
                )

            else:

                conflicting_names.append(
                    vote["strategy"]
                )


        return StrategyCouncilResult(

            strategies=strategies,

            strategy_votes=strategy_votes,

            consensus_action=decision,

            consensus_confidence=round(
                confidence,
                2
            ),

            supporting_strategies=supporting_names,

            conflicting_strategies=conflicting_names,

            strategy_weights=strategy_weights,

            weighted_support=weighted_support,

            top_strategy=top_strategy,

            explanation=(
                f"Consensus reached on {decision} "
                f"with confidence {round(confidence,2)}"
            )
        )