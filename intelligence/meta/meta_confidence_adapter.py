class MetaConfidenceAdapter:


    def adjust(
        self,
        confidence,
        meta_learning
    ):

        if not meta_learning:

            return confidence


        if isinstance(meta_learning, dict):

            adjustment = meta_learning.get(
                "confidence_adjustment",
                0
            )

        else:

            adjustment = getattr(
                meta_learning,
                "confidence_adjustment",
                0
            )


        adjusted_confidence = (
            confidence + adjustment
        )


        if adjusted_confidence < 0:

            adjusted_confidence = 0


        if adjusted_confidence > 100:

            adjusted_confidence = 100


        return adjusted_confidence