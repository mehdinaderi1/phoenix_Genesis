import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(__file__)
    )
)


from analysis.technical_engine import TechnicalEngine



def test_macd():

    print("\n🦅 Testing Phoenix MACD Engine")


    prices = [
        100,
        102,
        104,
        106,
        108,
        110,
        112,
        114,
        116,
        118,
        120,
        122,
        124,
        126,
        128,
        130,
        132,
        134,
        136,
        138,
        140,
        142,
        144,
        146,
        148,
        150
    ]


    engine = TechnicalEngine()


    macd = engine.calculate_macd(
        prices
    )


    assert macd is not None


    print("MACD:", macd)
    print("✅ MACD Passed")



def test_macd_positive_for_rising_prices():
    prices = [100 + 2 * i for i in range(40)]
    macd = TechnicalEngine().calculate_macd(prices)
    assert macd is not None
    assert macd > 0


def test_macd_negative_for_falling_prices():
    prices = [200 - 2 * i for i in range(40)]
    macd = TechnicalEngine().calculate_macd(prices)
    assert macd is not None
    assert macd < 0


if __name__ == "__main__":

    test_macd()