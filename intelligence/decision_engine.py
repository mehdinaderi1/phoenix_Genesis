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
                    self.rules.consensus_is_valid(report),
                    
                "signal":
                    getattr(report, "signal", None)
                    in ["BUY", "SELL"],

                "risk":
                    getattr(report, "risk", None)
                    == "LOW",

                "confidence":
                    getattr(report, "confidence", 0)
                    >= 80    

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

        metadata["champion_strategy"] = getattr(
            report,
            "champion_strategy",
            None
        )


        explanation = self._build_explanation(
            report
        )

        operational_strategy = getattr(
            report,
            "operational_strategy_result",
            None
        )

        strategy_allows_long = True
        strategy_allows_short = True

        if operational_strategy is not None:
            matched = operational_strategy.get("matched", False)
            strategy_signal = operational_strategy.get("signal")

            if not matched:
                strategy_allows_long = False
                strategy_allows_short = False
            else:
                strategy_allows_long = strategy_signal == "BUY"
                strategy_allows_short = strategy_signal == "SELL"

        can_long = (
            strategy_allows_long
            and self.rules.can_long(report)
        )
        can_short = (
            strategy_allows_short
            and self.rules.can_short(report)
        )
        
        print(
            "CAN SHORT:",
            can_short
        )

        print(
            "SHORT CHECK:",
            {
                "strategy_valid": self.rules.strategy_is_valid(report),
                "consensus_valid": self.rules.consensus_is_valid(report),
                "signal": report.signal,
                "risk": report.risk,
                "confidence": report.confidence,
            }
        )
        
        print(
            "CAN LONG:",
            self.rules.can_long(report)
        )

        print(
            "LONG CHECK:",
            {
                "strategy_valid": self.rules.strategy_is_valid(report),
                "consensus_valid": self.rules.consensus_is_valid(report),
                "signal": report.signal,
                "risk": report.risk,
                "confidence": report.confidence,
            }
        )


        if can_long:

            return DecisionResult(

                action="PREPARE_LONG",

                reason=
                    "Strong bullish signal with strategy consensus",

                confidence=
                    report.confidence,

                regime=
                    getattr(
                        report,
                        "regime",
                        None
                    ),

                signal=
                    getattr(
                        report,
                        "signal",
                        None
                    ),

                risk=
                    getattr(
                        report,
                        "risk",
                        None
                    ),

                trace=
                    self._build_trace(
                        report,
                        "PREPARE_LONG",
                        explanation
                    ),


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



        elif can_short:

            return DecisionResult(

                action="PREPARE_SHORT",

                reason=
                    "Bearish market conditions with strategy consensus",

                confidence=
                    report.confidence,

                regime=
                    getattr(
                        report,
                        "regime",
                        None
                    ),

                signal=
                    getattr(
                        report,
                        "signal",
                        None
                    ),

                risk=
                    getattr(
                        report,
                        "risk",
                        None
                    ),

                trace=
                    self._build_trace(
                        report,
                        "PREPARE_SHORT",
                        explanation
                    ),


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

                regime=
                    getattr(
                        report,
                        "regime",
                        None
                    ),

                signal=
                    getattr(
                        report,
                        "signal",
                        None
                    ),

                risk=
                    getattr(
                        report,
                        "risk",
                        None
                    ),

                trace=
                    self._build_trace(
                        report,
                        "WAIT",
                        explanation
                    ),

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
