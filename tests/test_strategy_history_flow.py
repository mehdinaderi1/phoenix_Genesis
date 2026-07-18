from intelligence.flow import IntelligenceFlow



def test_strategy_history_created_in_flow():

    flow = IntelligenceFlow()


    assert flow.strategy_history is not None