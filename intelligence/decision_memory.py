class DecisionMemory:

    def __init__(self):
        self.records = []


    def store(self, record):

        self.records.append(record)

        return record


    def get_all(self):

        return self.records


    def get_latest(self):

        if not self.records:
            return None

        return self.records[-1]


    def count(self):

        return len(self.records)