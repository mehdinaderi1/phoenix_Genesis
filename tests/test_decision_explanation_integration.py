from intelligence.decision_engine import DecisionEngine
from intelligence.report import MarketReport



def test_decision_result_contains_strategy_explanation():

    engine = DecisionEngine()


    report = MarketReport(

        symbol="BTCUSDT",

        timeframe="30m",

        trend="UP",

        regime="BULL",

        signal="BUY",

        confidence=90,

        risk="LOW",

        reasons=[],

        strategy_consensus={

            "decision": "BUY",

            "supporting_strategies": 3,

            "opposing_strategies": 1,

            "confidence": 0.85,

            "top_strategy":
                "momentum_v2"
        }
    )



    result = engine.decide(
        report
    )



    assert (
        result.action
        ==
        "PREPARE_LONG"
    )


    assert (
        result.explanation["decision"]
        ==
        "BUY"
    )


    assert (
        result.explanation["dominant_strategy"]
        ==
        "momentum_v2"
    )


    assert (
        result.explanation["confidence"]
        ==
        0.85
    )