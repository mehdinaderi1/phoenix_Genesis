from intelligence.lifecycle.lifecycle_metrics import (
    LifecycleMetrics
)


class LifecycleMetricsEngine:


    def calculate(self, history):

        events = history.events


        total_events = len(events)

        transitions = len(
            [
                event
                for event in events
                if event.from_state != event.to_state
            ]
        )


        if events:

            latest = events[-1]

            strategy_name = latest.strategy_name

            current_state = latest.to_state

        else:

            strategy_name = "UNKNOWN"

            current_state = "UNKNOWN"



        if current_state == "CHAMPION":

            score = 100
            health = "EXCELLENT"

        elif current_state == "ACTIVE":

            score = 20
            health = "GOOD"

        elif current_state == "CANDIDATE":

            score = 20
            health = "STABLE"

        elif current_state == "RETIRED":

            score = 0
            health = "ENDED"

        else:

            score = 0
            health = "UNKNOWN"



        return LifecycleMetrics(

            strategy_name=strategy_name,

            total_events=total_events,

            transitions=transitions,

            current_state=current_state,

            lifecycle_score=score,

            health=health

        )