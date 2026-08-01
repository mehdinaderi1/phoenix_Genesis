from intelligence.lifecycle.lifecycle_metrics import (
    LifecycleMetrics
)



class LifecycleAnalytics:


    def analyze(
        self,
        strategy_name,
        history
    ):


        events = [

            event

            for event in history.get_all()

            if event.strategy_name == strategy_name

        ]


        if not events:

            return LifecycleMetrics(

                strategy_name=strategy_name,

                total_events=0,

                transitions=0,

                current_state="UNKNOWN",

                lifecycle_score=0,

                health="UNKNOWN"

            )



        current_state = events[-1].to_state


        transitions = len(events)



        score = min(
            transitions * 20,
            100
        )


        if current_state == "ACTIVE":

            health = "GOOD"

        elif current_state == "CHAMPION":

            health = "EXCELLENT"

        elif current_state == "RETIRED":

            health = "ENDED"

        else:

            health = "STABLE"



        return LifecycleMetrics(

            strategy_name=strategy_name,

            total_events=len(events),

            transitions=transitions,

            current_state=current_state,

            lifecycle_score=score,

            health=health

        )