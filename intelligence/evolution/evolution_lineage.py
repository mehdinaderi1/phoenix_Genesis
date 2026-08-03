class EvolutionLineage:

    def __init__(self):
        self.nodes = []


    def add(
        self,
        record
    ):
        self.nodes.append(
            record
        )


    def all(self):

        return self.nodes


    def _child(
        self,
        record
    ):
        return getattr(
            record,
            "child",
            getattr(
                record,
                "child_strategy",
                None
            )
        )


    def _parent(
        self,
        record
    ):
        return getattr(
            record,
            "parent",
            getattr(
                record,
                "parent_strategy",
                None
            )
        )


    def find_lineage(
        self,
        strategy
    ):

        result = []

        current = strategy


        while current:

            found = None


            for record in self.nodes:

                if self._child(record) == current:

                    found = record
                    break


            if not found:
                break


            result.insert(
                0,
                found
            )


            current = self._parent(
                found
            )


        return result



    def children(
        self,
        strategy
    ):

        return [

            record

            for record in self.nodes

            if self._parent(record) == strategy

        ]



    def latest(
        self,
        strategy
    ):

        lineage = self.find_lineage(
            strategy
        )

        if not lineage:
            return None


        return lineage[-1]