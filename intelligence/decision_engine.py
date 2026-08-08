from intelligence.decision import DecisionResult
from intelligence.decision_rules import DecisionRules
from intelligence.decision_trace import DecisionTrace
from intelligence.strategy_consensus_explanation_builder import (
    StrategyConsensusExplanationBuilder
)


class DecisionEngine:


    def __init__(self):

        self.rules = DecisionRules()

        self.explanation_builder = (
            StrategyConsensusExplanationBuilder()
        )



    def _consensus_metadata(
        self,
        report
    ):

        consensus = getattr(
            report,
            "strategy_consensus",
            None
        )


        if not consensus:
            return {}


        return {

            "consensus_confidence":
                consensus.get(
                    "confidence",
                    0.0
                ),

            "supporting_strategies":
                consensus.get(
                    "supporting_strategies",
                    0
                ),

            "opposing_strategies":
                consensus.get(
                    "opposing_strategies",
                    0
                ),

            "top_strategy":
                consensus.get(
                    "top_strategy"
                )
        }

    def _build_trace(
        self,
        report,
        action,
        explanation
    ):

        trace = DecisionTrace(

            decision=action,

            signal=getattr(
                report,
                "signal",
                None
            ),

            confidence=report.confidence,

            risk=getattr(
                report,
                "risk",
                "UNKNOWN"
            ),

            strategy_consensus=getattr(
                report,
                "strategy_consensus",
                {}
            ),

            gates={

                "strategy":
                    self.rules.strategy_is_valid(report),

                "consensus":
                    self.rules.consensus_is_valid(report)

            },

            explanation=explanation

        )

        return trace.to_dict()



    def _build_explanation(
        self,
        report
    ):

        consensus = getattr(
            report,
            "strategy_consensus",
            None
        )


        if not consensus:
            return {}


        explanation = (
            self.explanation_builder.build(
                consensus
            )
        )


        return explanation.to_dict()



    def decide(
        self,
        report
    ):


        metadata = self._consensus_metadata(
            report
        )


        explanation = self._build_explanation(
            report
        )



        if self.rules.can_long(report):

            return DecisionResult(

                action="PREPARE_LONG",

                reason=
                    "Strong bullish signal with strategy consensus",

                confidence=
                    report.confidence,

                explanation=
                    explanation,

                metadata={
                    **metadata,
                    "trace": self._build_trace(
                        report,
                        "PREPARE_LONG",
                        explanation
                    )
                },

                **metadata
            )



        elif self.rules.can_short(report):

            return DecisionResult(

                action="PREPARE_SHORT",

                reason=
                    "Bearish market conditions with strategy consensus",

                confidence=
                    report.confidence,

                explanation=
                    explanation,

                metadata={
                    **metadata,
                    "trace": self._build_trace(
                        report,
                        "PREPARE_SHORT",
                        explanation
                    )
                },

                **metadata
            )



        else:

            return DecisionResult(

                action="WAIT",

                reason=
                    "Market conditions require monitoring",

                confidence=
                    report.confidence,

                explanation=
                    explanation,

                metadata={
                    **metadata,
                    "trace": self._build_trace(
                        report,
                        "WAIT",
                        explanation
                    )
                },

                **metadata
            )