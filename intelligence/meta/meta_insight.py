class MetaInsight:

    def __init__(
        self,
        samples=0,
        average_quality=0,
        confidence_accuracy=0,
        reliability="UNKNOWN",
        bias="UNKNOWN"
    ):

        self.samples = samples

        self.average_quality = (
            average_quality
        )

        self.confidence_accuracy = (
            confidence_accuracy
        )

        self.reliability = reliability

        self.bias = bias