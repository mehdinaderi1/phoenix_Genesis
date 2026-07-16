from intelligence.intelligence_report_generator import IntelligenceReportGenerator
from intelligence.decision_record import DecisionRecord



def test_intelligence_report():


    records = [

        DecisionRecord(

            symbol="BTCUSDT",

            timeframe="Multi",

            regime="TRENDING_BULLISH",

            signal="BUY",

            confidence=85,

            risk="LOW",

            action="PREPARE_LONG",

            validation_status="APPROVED",

            quality_score=100
        ),


        DecisionRecord(

            symbol="BTCUSDT",

            timeframe="Multi",

            regime="RANGING",

            signal="SELL",

            confidence=60,

            risk="MEDIUM",

            action="WAIT",

            validation_status="REJECTED",

            quality_score=40
        )

    ]



    generator = IntelligenceReportGenerator()


    report = generator.generate(records)



    assert report.total_decisions == 2

    assert report.approval_rate == 50

    assert report.average_quality == 70

    assert report.best_action == "PREPARE_LONG"

    assert report.best_regime == "TRENDING_BULLISH"