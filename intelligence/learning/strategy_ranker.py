class StrategyRanker:


    def rank(
        self,
        strategies
    ):

        if not strategies:

            return []


        return sorted(
            strategies,
            key=lambda x: x.get("score", 0),
            reverse=True
        )



    def best(
        self,
        strategies
    ):

        ranked = self.rank(
            strategies
        )

        if not ranked:

            return None


        return ranked[0]