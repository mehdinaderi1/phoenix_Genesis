"""
Evolution Governance

Validates evolution records before acceptance.
"""


class EvolutionGovernance:
    """
    Governance layer for strategy evolution.

    Checks:
    - performance improvement
    - valid lineage
    - generation consistency
    """


    def evaluate(self, record):
        """
        Evaluate EvolutionRecord.
        """


        if record.score_after <= record.score_before:
            return {
                "status": "REJECTED",
                "reason": "No performance improvement"
            }


        if not record.parent or not record.child:
            return {
                "status": "REJECTED",
                "reason": "Invalid lineage"
            }


        if record.generation < 1:
            return {
                "status": "REJECTED",
                "reason": "Invalid generation"
            }


        return {
            "status": "APPROVED",
            "reason": "Evolution validated"
        }