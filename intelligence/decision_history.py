from intelligence.decision_record import DecisionRecord


class DecisionHistory:

    def __init__(self):

        self.records = []


    def add(self, record: DecisionRecord):

        self.records.append(record)


    def get_all(self):

        return self.records


    def get_latest(self):

        if not self.records:
            return None

        return self.records[-1]


    def find_by_symbol(self, symbol):

        return [
            record
            for record in self.records
            if record.symbol == symbol
        ]