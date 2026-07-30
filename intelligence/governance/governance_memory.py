class GovernanceMemory:


    def __init__(
        self
    ):

        self.records = []



    def store(
        self,
        record
    ):

        self.records.append(
            record
        )



    def get_all(
        self
    ):

        return self.records



    def count(
        self
    ):

        return len(
            self.records
        )



    def latest(
        self
    ):

        if not self.records:

            return None


        return self.records[-1]



    def find_by_status(
        self,
        status
    ):

        results = []


        for record in self.records:

            record_status = getattr(
                record,
                "status",
                None
            )


            if (
                record_status
                ==
                status
            ):

                results.append(
                    record
                )


        return results



    def find_similar(
        self,
        strategy
    ):

        results = []


        for record in self.records:

            record_strategy = getattr(
                record,
                "strategy",
                {}
            )


            if not isinstance(
                record_strategy,
                dict
            ):

                continue


            matched = True


            for key, value in strategy.items():

                if (
                    record_strategy.get(key)
                    !=
                    value
                ):

                    matched = False
                    break


            if matched:

                results.append(
                    record
                )


        return results