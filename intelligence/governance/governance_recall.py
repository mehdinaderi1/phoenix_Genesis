class GovernanceRecall:


    def __init__(
        self,
        memory
    ):

        self.memory = memory


    def find_similar(
        self,
        strategy
    ):

        records = self.memory.get_all()


        matches = []


        for record in records:

            if (
                record.strategy.get("risk")
                ==
                strategy.get("risk")
            ):

                matches.append(
                    record
                )


        return matches