class EvolutionRecall:


    def __init__(
        self,
        history
    ):

        self.history = history



    def find_lineage(
        self,
        strategy_name
    ):

        results = []


        records = self.history.get_all()


        for record in records:

            if record.parent == strategy_name:

                results.append(
                    record
                )


            if record.child == strategy_name:

                results.append(
                    record
                )


        return results



    def generations(
        self,
        strategy_name
    ):

        lineage = self.find_lineage(
            strategy_name
        )


        return len(lineage)