from dataclasses import dataclass


@dataclass(slots=True)
class EvolutionInsight:

    reason: str
    improvement: str
    confidence: float
    learning: bool


class StrategyEvolutionInsight:

    def analyze(
        self,
        old_strategy,
        new_strategy,
        performance,
        decision=None
    ):

        score = performance.get(
            "score",
            0
        )

        success_rate = performance.get(
            "success_rate",
            0
        )

        if decision == "IMPROVE":

            return EvolutionInsight(

                reason="Strategy needs improvement",

                improvement="Optimize strategy parameters",

                confidence=0.85,

                learning=True
            )

        if success_rate < 0.5:

            return EvolutionInsight(

                reason="Low success rate",

                improvement="Improve entry conditions",

                confidence=0.90,

                learning=True
            )

        if score < 60:

            return EvolutionInsight(

                reason="Low strategy score",

                improvement="Refine risk management",

                confidence=0.80,

                learning=True
            )

        return EvolutionInsight(

            reason="Stable strategy",

            improvement="No major changes",

            confidence=0.95,

            learning=False
        )