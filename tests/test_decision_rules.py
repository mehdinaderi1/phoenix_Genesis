from intelligence.decision_rules import DecisionRules
from intelligence.report import MarketReport



def test_long_rule():


    report = MarketReport(
        symbol="BTCUSDT",
        timeframe="Multi",
        trend="BULLISH",
        regime="TRENDING_BULLISH",
        signal="BUY",
        confidence=85,
        risk="LOW",
        reasons=[]
    )


    rules = DecisionRules()


    assert rules.can_long(report) == True