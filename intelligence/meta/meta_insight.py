class MetaInsight:


    def __init__(
        self,
        samples=0,
        average_quality=0,
        confidence_accuracy=0,
        reliability="UNKNOWN",
        bias=None,
        meta_feedback=None
    ):

        self.samples = samples

        self.average_quality = average_quality

        self.confidence_accuracy = confidence_accuracy

        self.reliability = reliability

        self.bias = bias or {
            "bias": "UNKNOWN"
        }

        self.meta_feedback = (
            meta_feedback
        )



    def __getitem__(self, key):

        if key == "bias":

            return self.bias


        return getattr(
            self,
            key
        )