from intelligence.lifecycle.lifecycle_evolution_repository import (
    LifecycleEvolutionRepository
)


def test_save_evolution_record():

    repository = LifecycleEvolutionRepository()

    record = {
        "strategy": "Strategy_v2",
        "action": "IMPROVE",
        "status": "EVOLVED"
    }

    result = repository.save(record)

    assert result == record
    assert len(repository.records) == 1



def test_get_all_records():

    repository = LifecycleEvolutionRepository()

    repository.save({
        "strategy": "Strategy_v2",
        "action": "IMPROVE"
    })

    repository.save({
        "strategy": "Strategy_v3",
        "action": "IMPROVE"
    })


    records = repository.get_all()

    assert len(records) == 2



def test_get_latest_record():

    repository = LifecycleEvolutionRepository()

    repository.save({
        "strategy": "Strategy_v2"
    })

    repository.save({
        "strategy": "Strategy_v3"
    })


    latest = repository.get_latest()

    assert latest["strategy"] == "Strategy_v3"



def test_find_strategy_history():

    repository = LifecycleEvolutionRepository()


    repository.save({
        "strategy": "Strategy_v2",
        "action": "IMPROVE"
    })

    repository.save({
        "strategy": "Strategy_v3",
        "action": "IMPROVE"
    })

    repository.save({
        "strategy": "OtherStrategy",
        "action": "KEEP"
    })


    result = repository.find_by_strategy(
        "Strategy_v2"
    )


    assert len(result) == 1
    assert result[0]["action"] == "IMPROVE"