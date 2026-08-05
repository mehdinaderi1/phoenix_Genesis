from intelligence.decision_engine import DecisionEngine


class MockReport:

    def __init__(
        self,
        signal,
        risk,
        confidence,
        champion_strategy
    ):

        self.signal = signal

        self.risk = risk

        self.confidence = confidence

        self.champion_strategy = champion_strategy



def test_decision_accepts_active_champion_strategy():

    report = MockReport(
        signal="BUY",
        risk="LOW",
        confidence=90,
        champion_strategy={
            "name": "trend_following",
            "status": "ACTIVE",
            "score": 90,
            "success_rate": 85
        }
    )


    engine = DecisionEngine()


    decision = engine.decide(
        report
    )


    assert decision.action == "PREPARE_LONG"



def test_decision_rejects_invalid_strategy():

    report = MockReport(
        signal="BUY",
        risk="LOW",
        confidence=90,
        champion_strategy={
            "name": "old_strategy",
            "status": "RETIRED",
            "score": 95,
            "success_rate": 90
        }
    )


    engine = DecisionEngine()


    decision = engine.decide(
        report
    )


    assert decision.action != "PREPARE_LONG"