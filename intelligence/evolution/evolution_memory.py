from intelligence.evolution.evolution_lineage import (
    EvolutionLineage
)


class EvolutionMemory:


    def __init__(
        self
    ):

        self.records = []

        self.lineage = EvolutionLineage()



    def store(
        self,
        record
    ):

        self.records.append(
            record
        )

        self.lineage.add(
            record
        )



    def all(
        self
    ):

        return self.records



    def count(
        self
    ):

        return len(
            self.records
        )



    def recall(
        self,
        strategy
    ):

        return [

            record

            for record in self.records

            if (
                record.child == strategy
                or
                record.parent == strategy
            )

        ]



    def get_lineage(
        self,
        strategy
    ):

        return self.lineage.find_lineage(
            strategy
        )



    def children(
        self,
        strategy
    ):

        return self.lineage.children(
            strategy
        )



    def latest(
        self,
        strategy
    ):

        return self.lineage.latest(
            strategy
        )



    def best(
        self,
        strategy
    ):

        records = self.recall(
            strategy
        )


        if not records:
            return None


        return max(
            records,
            key=lambda r: r.score_after
        )