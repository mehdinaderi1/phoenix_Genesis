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