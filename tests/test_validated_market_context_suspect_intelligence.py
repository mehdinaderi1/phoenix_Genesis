from core.database import DatabaseManager
from core.market_data.operational_intelligence_runtime import OperationalIntelligenceRuntime


class SuspectMarketContextRuntime:
    def __init__(self):
        self.calls = 0

    def run(self, symbol="BTCUSDT", cycles=1):
        self.calls += 1
        return []


class FailingIntelligenceFlow:
    def create_report(self, consensus):
        raise AssertionError(
            "Intelligence must not run for SUSPECT market context"
        )


def test_suspect_market_context_does_not_reach_intelligence(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    market_context_runtime = SuspectMarketContextRuntime()

    runtime = OperationalIntelligenceRuntime(
        market_context_runtime=market_context_runtime,
        intelligence_flow=FailingIntelligenceFlow(),
    )

    results = runtime.run(
        symbol="BTCUSDT",
        cycles=1,
    )

    assert market_context_runtime.calls == 1
    assert results == []

    database.close()
