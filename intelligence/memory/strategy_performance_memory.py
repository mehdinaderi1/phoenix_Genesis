from intelligence.performance_record import PerformanceRecord
from intelligence.memory import _persistence


class StrategyPerformanceMemory:

    def __init__(self, path=None):
        self.path = path if path is not None else None
        if self.path is None:
            self.records = []
        else:
            raw = _persistence.load_records(self.path)
            self.records = [
                _persistence.reconstruct(PerformanceRecord, d)
                for d in raw
            ]

    def save_performance(self, performance: PerformanceRecord):
        self.records.append(performance)
        if self.path is not None:
            _persistence.append_record(self.path, performance)

    def get_performances(self):
        return self.records

    def find_by_strategy(self, strategy: str):
        return [
            record for record in self.records
            if record.strategy == strategy
        ]

    def find_similar(self, strategy: str, success=None):
        results = []
        for record in self.records:
            if record.strategy != strategy:
                continue
            if success is not None and record.success != success:
                continue
            results.append(record)
        return results