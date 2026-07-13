import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(__file__)
    )
)


from analysis.technical_engine import TechnicalEngine



def test_rsi():

    print("\n🦅 Testing Phoenix RSI Engine")


    prices = [
        100,
        102,
        104,
        103,
        105,
        107,
        106,
        108,
        110,
        109,
        111,
        113,
        112,
        114,
        116
    ]


    engine = TechnicalEngine()


    rsi = engine.calculate_rsi(
        prices,
        14
    )


    assert rsi is not None


    print("RSI:", rsi)
    print("✅ RSI Passed")



if __name__ == "__main__":

    test_rsi()