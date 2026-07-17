class StrategyMemory:


    def __init__(self):

        self.records = []


    def store(self, strategy_record):

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