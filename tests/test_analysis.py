import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(__file__)
    )
)


from analysis.technical_engine import TechnicalEngine



def test_moving_average():

    print("\n🦅 Testing Phoenix Analysis Engine")


    prices = [
        64000,
        64500,
        65000,
        65500,
        66000
    ]


    engine = TechnicalEngine()


    ma = engine.calculate_ma(
        prices,
        5
    )


    assert ma == 65000


    print("✅ Moving Average Passed")



if __name__ == "__main__":

    test_moving_average()