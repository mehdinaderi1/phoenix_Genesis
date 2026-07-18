from intelligence.learning.strategy_history import StrategyHistory



def test_strategy_history_stores_versions():

    history = StrategyHistory()


    history.add_record(
        "Trend",
        60,
        0.55,
        20
    )

    history.add_record(
        "Trend",
        80,
        0.7,
        50
    )


    records = history.get_history(
        "Trend"
    )


    assert len(records) == 2

    assert records[0]["version"] == 1

    assert records[1]["version"] == 2



def test_strategy_history_detects_improvement():

    history = StrategyHistory()


    history.add_record(
        "Trend",
        60
    )

    history.add_record(
        "Trend",
        75
    )


    assert history.trend(
        "Trend"
    ) == "IMPROVING"