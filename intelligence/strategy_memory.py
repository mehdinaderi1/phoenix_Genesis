class StrategyMemory:


    def __init__(self):

        self.records = []



    def store(
        self,
        strategy_record
    ):

        self.records.append(
            strategy_record
        )



    def count(self):

        return len(self.records)



    def latest(self):

        if not self.records:

            return None

        return self.records[-1]



    def find_by_pattern(
        self,
        regime,
        signal,
        risk
    ):

        results = []

        for record in self.records:

            if (
                record.get("regime") == regime
                and record.get("signal") == signal
                and record.get("risk") == risk
            ):

                results.append(record)


        return results



    def update_strategy(
        self,
        new_strategy
    ):

        for index, record in enumerate(self.records):

            if (
                record.get("strategy")
                == new_strategy.get("strategy")
            ):

                old_score = record.get(
                    "score",
                    0
                )

                new_score = new_strategy.get(
                    "score",
                    0
                )


                if new_score > old_score:

                    self.records[index] = new_strategy

                    return True


                return False


        return False