from intelligence.pattern_confidence_analyzer import PatternConfidenceAnalyzer


class PatternService:


    def __init__(self):

        self.analyzer = PatternConfidenceAnalyzer()



    def find_best_pattern(self, patterns):


        if not patterns:

            return None


        ranked = self.analyzer.analyze(patterns)


        return max(

            ranked,

            key=lambda x: x.confidence

        )