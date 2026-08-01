"""
Lifecycle Evolution Repository

Stores and retrieves lifecycle evolution events.
"""


class LifecycleEvolutionRepository:
    """
    Persistence layer for lifecycle evolution records.

    Responsible for:
    - saving evolution events
    - retrieving evolution history
    - tracking strategy lineage
    """

    def __init__(self):
        self.records = []


    def save(self, record):
        """
        Store lifecycle evolution record.
        """

        self.records.append(record)

        return record


    def get_all(self):
        """
        Return all lifecycle evolution records.
        """

        return self.records


    def get_latest(self):
        """
        Return latest evolution record.
        """

        if not self.records:
            return None

        return self.records[-1]


    def find_by_strategy(self, strategy_name):
        """
        Find evolution records by strategy
        or parent strategy lineage.
        """

        return [
            record
            for record in self.records
            if (
                record.get("strategy") == strategy_name
                or
                record.get("parent_strategy") == strategy_name
            )
        ]