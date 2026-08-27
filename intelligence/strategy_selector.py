class StrategySelector:


    def __init__(
        self,
        strategy_recall,
        strategy_ranking       
    ):

        self.strategy_recall = strategy_recall

        self.strategy_ranking = strategy_ranking

      
    def select_with_result(
        self,
        regime,
        signal,
        risk
    ):

        strategies = self.strategy_recall.recall(
            regime,
            signal,
            risk
        )


        if not strategies:

            return None



        if hasattr(
            self.strategy_ranking,
            "rank_with_result"
        ):

            ranking_result = (
                self.strategy_ranking.rank_with_result(
                    strategies,
                    market_context={
                        "regime": regime,
                        "signal": signal,
                        "risk": risk
                    }
                )
            )


        else:

            ranking_result = (
                self.strategy_ranking.rank(
                    strategies
                )
            )



        if not ranking_result:

            return None



        champion = None



        if hasattr(
            ranking_result,
            "top_strategy"
        ):

            champion_item = (
                ranking_result.top_strategy
            )


            if champion_item:

                champion = (
                    champion_item.strategy_record
                )


        else:

            if ranking_result:

                champion = ranking_result[0]



        if not champion:

            return None

        
        return {
            "champion": champion,
            "ranking": ranking_result
        }



    def select(
        self,
        regime,
        signal,
        risk
    ):

        result = self.select_with_result(
            regime,
            signal,
            risk
        )


        if not result:

            return None


        return result["champion"]