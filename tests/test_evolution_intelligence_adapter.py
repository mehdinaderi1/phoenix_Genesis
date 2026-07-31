from intelligence.evolution.evolution_intelligence_adapter import (
    EvolutionIntelligenceAdapter
)



class DummySelector:


    def select(
        self,
        lineages
    ):

        return {

            "lineage": "best_strategy",

            "analysis": {

                "score": 20

            }

        }



def test_evolution_adapter():


    adapter = EvolutionIntelligenceAdapter(
        DummySelector()
    )


    result = adapter.analyze(
        [
            "strategy"
        ]
    )


    assert result["available"] is True

    assert result["analysis"]["score"] == 20