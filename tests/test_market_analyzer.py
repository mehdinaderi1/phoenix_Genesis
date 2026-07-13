import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(__file__)
    )
)


from analysis.market_analyzer import MarketAnalyzer



def test_market_analyzer():

    print("\n🦅 Testing Phoenix Market Analyzer")


    prices = [

    64000,
    64200,
    64500,
    64800,
    65000,
    65200,
    65500,
    65800,
    66000,
    66300,
    66500,
    66800,
    67000,
    67200,
    67500,
    67800,
    68000,
    68300,
    68500,
    68800,
    69000,
    69300,
    69500,
    69800,
    70000,
    70200,
    70500,
    70800,
    71000,
    71200

]


    analyzer = MarketAnalyzer()


    result = analyzer.analyze(
        prices
    )


    assert result["ma"] is not None
    assert result["rsi"] is not None
    assert result["macd"] is not None


    print(result)

    print("MACD:", result["macd"])

    print("✅ Market Analyzer Passed")



if __name__ == "__main__":

    test_market_analyzer()