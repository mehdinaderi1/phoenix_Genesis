from intelligence.evolution.evolution_governance import (
    EvolutionGovernance,
)



class DummyIntelligence:


    def evaluate(
        self,
        strategy
    ):

        return {

            "decision": "ALLOW"

        }




class DummyGovernance:


    def evaluate(
        self,
        strategy
    ):

        return {

            "status": "APPROVED"

        }



def test_evolution_governance_allows():


    bridge = EvolutionGovernance(

        DummyIntelligence(),

        DummyGovernance()

    )


    result = bridge.evaluate(
        "trend_v1"
    )


    assert result["status"] == "APPROVED"



class BlockIntelligence:


    def evaluate(
        self,
        strategy
    ):

        return {

            "decision": "BLOCK"

        }



def test_evolution_governance_blocks_bad_evolution():


    bridge = EvolutionGovernance(

        BlockIntelligence(),

        DummyGovernance()

    )


    result = bridge.evaluate(
        "bad_strategy"
    )


    assert result["status"] == "BLOCKED"