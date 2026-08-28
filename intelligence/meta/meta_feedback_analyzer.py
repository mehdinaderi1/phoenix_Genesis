class MetaFeedbackAnalyzer:


    def analyze(
        self,
        records
    ):

        if not records:

            return {

                "samples": 0,

                "successful_adjustments": 0,

                "average_adjustment": 0,

                "reliability": "UNKNOWN"

            }


        samples = len(records)


        successful = sum(
            1
            for record in records
            if record.meta_effective
        )


        average_adjustment = (
            sum(
                record.adjustment
                for record in records
            )
            /
            samples
        )


        success_rate = (
            successful / samples
        )


        if success_rate >= 0.6:

            reliability = "HIGH"


        elif success_rate >= 0.4:

            reliability = "MEDIUM"


        else:

            reliability = "LOW"



        return {

            "samples": samples,

            "successful_adjustments": successful,

            "average_adjustment": average_adjustment,

            "success_rate": success_rate,

            "reliability": reliability

        }