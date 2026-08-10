class StrategyMemory:


    def __init__(self):

        self.records = []



    def store(
        self,
        strategy_record
    ):

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

        regime = str(regime).upper()
        signal = str(signal).upper()
        risk = str(risk).upper()


        results = []

        for record in self.records:

            record_regime = str(
                record.get("regime", "")
            ).upper()

            record_signal = str(
                record.get("signal", "")
            ).upper()

            record_risk = str(
                record.get("risk", "")
            ).upper()

            if (
                record_regime == regime
                and record_signal == signal
                and record_risk == risk
            ):

                results.append(record)


        return results



    def update_strategy(
        self,
        new_strategy
    ):

        for index, record in enumerate(self.records):

            if (
                record.get("strategy")
                == new_strategy.get("strategy")
            ):

                old_score = record.get(
                    "score",
                    0
                )

                new_score = new_strategy.get(
                    "score",
                    0
                )


                if new_score > old_score:

                    updated = record.copy()

                    updated.update(
                        new_strategy
                    )

                    self.records[index] = updated

                    return True

                return False


        return False