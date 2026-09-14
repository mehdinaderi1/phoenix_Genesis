from intelligence.consensus import ConsensusResult

from core.market_data.operational_intelligence_context import (
    OperationalIntelligenceContext
)


class OperationalIntelligenceAdapter:
    """Adapts operational intelligence context to the existing consensus contract."""

    def to_consensus(self, context):
        if context is None:
            raise ValueError("context must not be None")

        if not isinstance(context, OperationalIntelligenceContext):
            raise TypeError(
                "context must be an OperationalIntelligenceContext"
            )

        return ConsensusResult(
            trend=context.trend,
            signal=context.signal,
            confidence=context.confidence
        )
