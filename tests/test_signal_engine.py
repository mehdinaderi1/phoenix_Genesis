from analysis.signal_engine import SignalEngine


def test_signal():

    analyzer = SignalEngine()

    data = {
        "ma": 70740,
        "rsi": 100,
        "macd": 1745
    }

    result = analyzer.analyze(data)

    print(result)

    assert len(result) > 0

    print("✅ Signal Engine Passed")


test_signal()