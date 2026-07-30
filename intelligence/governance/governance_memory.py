class GovernanceMemory:


    def __init__(self):

        self.records = []


    def store(
        self,
        record
    ):

        self.records.append(
            record
        )


    def count(self):

        return len(
            self.records
        )


    def get_all(
        self
    ):

        return self.records


    def latest(self):

        if not self.records:
            return None

        return self.records[-1]


    def find_by_status(
        self,
        status
    ):

        return [
            record
            for record in self.records
            if record.status == status
        ]