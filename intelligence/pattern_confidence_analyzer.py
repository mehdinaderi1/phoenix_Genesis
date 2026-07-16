from intelligence.pattern_confidence import PatternConfidence


class PatternConfidenceAnalyzer:


    def analyze(self, ranked_patterns):


        results = []


        for pattern in ranked_patterns:


            confidence = pattern.score


            if pattern.reliability == "HIGH":

                confidence += 10


            elif pattern.reliability == "MEDIUM":

                confidence += 5



            if confidence > 100:

                confidence = 100



            results.append(

                PatternConfidence(

                    regime=pattern.regime,

                    action=pattern.action,

                    confidence=confidence,

                    reliability=pattern.reliability,

                    samples=pattern.samples,

                    score=pattern.score

                )

            )


        return results