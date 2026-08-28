class MetaMemory:


    def __init__(self):

        self.records = []


    def store(
        self,
        record
    ):

        self.records.append(
            record
        )


    def get_records(
        self
    ):

        return self.records


    def count(
        self
    ):

        return len(
            self.records
        )