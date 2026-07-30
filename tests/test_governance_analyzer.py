from intelligence.governance.governance_analyzer import (
    GovernanceAnalyzer
)


def test_governance_analyzer_stable():

    analyzer = GovernanceAnalyzer()


    result = analyzer.analyze(
        [
            {
                "confidence": 10
            },
            {
                "confidence": 20
            }
        ]
    )


    assert result["status"] == "STABLE"



def test_governance_analyzer_review():

    analyzer = GovernanceAnalyzer()


    result = analyzer.analyze(
        [
            {
                "confidence": 0
            },
            {
                "confidence": 0
            }
        ]
    )


    assert result["status"] == "REVIEW"