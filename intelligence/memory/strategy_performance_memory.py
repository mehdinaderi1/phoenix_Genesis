from intelligence.performance_record import PerformanceRecord


class StrategyPerformanceMemory:

    def __init__(self):
        self.records = []


    def save_performance(
        self,
        performance: PerformanceRecord
    ):
        self.records.append(
            performance
        )


    def get_performances(self):
        return self.records


    def find_by_strategy(
        self,
        strategy: str
    ):
        return [
            record
            for record in self.records
            if record.strategy == strategy
        ]


    def find_similar(
        self,
        strategy: str,
        success: bool | None = None
    ):
        results = []

        for record in self.records:

            if record.strategy != strategy:
                continue

            if success is not None:

                if record.success != success:
                    continue

            results.append(record)

        return results