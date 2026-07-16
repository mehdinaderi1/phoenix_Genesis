from intelligence.decision_pattern import DecisionPattern


class PatternAnalyzer:


    def analyze(self, records):


        if not records:

            return []


        patterns = {}


        for record in records:

            key = (
                record.regime,
                record.action
            )


            if key not in patterns:

                patterns[key] = []


            patterns[key].append(record)



        results = []


        for key, items in patterns.items():

            regime, action = key


            average_quality = sum(

                r.quality_score

                for r in items

            ) / len(items)



            results.append(

                DecisionPattern(

                    regime=regime,

                    action=action,

                    samples=len(items),

                    average_quality=average_quality

                )

            )


        return results