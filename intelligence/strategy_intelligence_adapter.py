from intelligence.learning.strategy_evolution_knowledge import (
    StrategyKnowledge
)

from intelligence.strategy_intelligence_context import (
    StrategyIntelligenceContext
)



class StrategyIntelligenceAdapter:


    def build_context(
        self,
        strategy,
        history
    ):

        if strategy is None:

            return None, None



        if not history:

            context = StrategyIntelligenceContext(

                strategy=strategy,

                confidence=0.0,

                reason="No evolution history",

                has_evolution_knowledge=False

            )


            return context, None



        generations = len(history)


        total_score = sum(
            item.score
            for item in history
        )


        total_success = sum(
            item.success_rate
            for item in history
        )


        knowledge = StrategyKnowledge(

            strategy=strategy,

            generations=generations,

            average_score=(
                total_score / generations
            ),

            average_success_rate=(
                total_success / generations
            ),

            improvements=sum(
                1
                for item in history
                if item.decision == "IMPROVE"
            ),

            retirements=sum(
                1
                for item in history
                if item.decision == "RETIRE"
            )

        )


        context = StrategyIntelligenceContext(

            strategy=strategy,

            confidence=(
                knowledge.average_score / 100
            ),

            reason=(
                "Built from evolution history"
            ),

            has_evolution_knowledge=True

        )


        return context, knowledge