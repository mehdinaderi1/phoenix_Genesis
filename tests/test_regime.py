from intelligence.regime import MarketRegime


def test_market_regime():

    regime = MarketRegime(
        regime="TRENDING_BULLISH",
        confidence=80,
        reasons=[
            "Bullish consensus",
            "Strong momentum"
        ]
    )

    assert regime.regime == "TRENDING_BULLISH"
    assert regime.confidence == 80
    assert len(regime.reasons) == 2