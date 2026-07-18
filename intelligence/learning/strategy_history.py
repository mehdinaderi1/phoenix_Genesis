class StrategyHistory:

    def __init__(self):
        self.history = {}


    def add_record(
        self,
        strategy,
        score,
        success_rate=0,
        samples=0
    ):

        if strategy not in self.history:
            self.history[strategy] = []


        record = {
            "version": len(self.history[strategy]) + 1,
            "score": score,
            "success_rate": success_rate,
            "samples": samples
        }


        self.history[strategy].append(record)


        return record



    def get_history(
        self,
        strategy
    ):

        return self.history.get(
            strategy,
            []
        )



    def latest(
        self,
        strategy
    ):

        records = self.get_history(
            strategy
        )

        if not records:
            return None


        return records[-1]



    def trend(
        self,
        strategy
    ):

        records = self.get_history(
            strategy
        )


        if len(records) < 2:
            return "UNKNOWN"


        if records[-1]["score"] > records[-2]["score"]:
            return "IMPROVING"


        if records[-1]["score"] < records[-2]["score"]:
            return "DECLINING"


        return "STABLE"