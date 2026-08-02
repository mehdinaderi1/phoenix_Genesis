class EvolutionConfidenceMemory:


    def __init__(
        self
    ):

        self.records = []


    def store(
        self,
        strategy,
        confidence
    ):

        record = {

            "strategy":
                strategy,

            "confidence":
                confidence

        }


        self.records.append(
            record
        )


        return record



    def all(
        self
    ):

        return self.records



    def count(
        self
    ):

        return len(
            self.records
        )



    def recall(
        self,
        strategy
    ):

        return [

            record

            for record in self.records

            if record["strategy"] == strategy

        ]



    def latest(
        self,
        strategy
    ):

        records = self.recall(
            strategy
        )


        if not records:

            return None


        return records[-1]



    def average_confidence(
        self,
        strategy
    ):

        records = self.recall(
            strategy
        )


        if not records:

            return 0


        return (

            sum(

                r["confidence"]

                for r in records

            )

            /

            len(records)

        )