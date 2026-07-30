class GovernanceHistory:


    def __init__(self):

        self.records = []



    def store(
        self,
        record
    ):

        self.records.append(
            record
        )



    def _to_dict(
        self,
        record
    ):

       
        return {
            "strategy": record.strategy,
            "status": record.status,
            "reason": record.reason
        }



    def get_all(
        self
    ):

        return [
            self._to_dict(record)
            for record in self.records
        ]



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


        return self._to_dict(
            self.records[-1]
        )



    def find_by_strategy(
        self,
        strategy_name
    ):

        result = []


        for record in self.records:

            strategy = record.strategy


            if isinstance(strategy, dict):

                name = strategy.get(
                    "name"
                )

            else:

                name = strategy



            if name == strategy_name:

                result.append(
                    self._to_dict(record)
                )


        return result



    def find_by_status(
        self,
        status
    ):

        return [
            self._to_dict(record)
            for record in self.records
            if record.status == status
        ]