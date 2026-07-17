from intelligence.pattern_cluster import PatternCluster
from intelligence.pattern_recognizer import PatternRecognizer


class PatternIntelligence:


    def __init__(self):

        self.clusterer = PatternCluster()

        self.recognizer = PatternRecognizer()



    def analyze(
        self,
        experiences
    ):

        clusters = self.clusterer.cluster(
            experiences
        )


        insights = []


        for pattern, items in clusters.items():

            result = self.recognizer.recognize(
                items
            )


            if result:

                result["pattern"] = pattern

                insights.append(
                    result
                )


        return insights