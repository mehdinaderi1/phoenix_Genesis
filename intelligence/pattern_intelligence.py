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

                parts = pattern.split("_")


                result["pattern"] = (
                    parts[0],
                    parts[1],
                    parts[2]
                )

                insights.append(
                    result
                )


        return insights