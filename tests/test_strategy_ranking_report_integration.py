from intelligence.consensus import ConsensusResult
from intelligence.flow import IntelligenceFlow
from intelligence.strategy_ranking_result import StrategyRankingResult
import intelligence.flow as flow_module
print("LOADED FLOW:", flow_module.__file__)


def test_strategy_ranking_report_integration():

    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )

    flow = IntelligenceFlow()


    print("FLOW MODULE:", IntelligenceFlow.__module__)
    print("FLOW FILE:", IntelligenceFlow.__file__ if hasattr(IntelligenceFlow, "__file__") else "NO FILE")

    flow.strategy_memory.store(
        {
            "name": "trend_following",
            "strategy": "trend_following",
            "regime": "TRENDING_BULLISH",
            "signal": "BUY",
            "risk": "LOW",
            "score": 90,
            "success_rate": 0.85,
            "status": "ACTIVE"
        }
    )

    report = flow.create_report(
        consensus
    )

    print("TYPE:", type(report))
    print("DICT:", isinstance(report, dict))
    print("ATTRS:", dir(report))

    assert report.strategy_ranking is not None

    assert isinstance(
        report.strategy_ranking,
        StrategyRankingResult
    )

    assert report.strategy_ranking.top_strategy is not None