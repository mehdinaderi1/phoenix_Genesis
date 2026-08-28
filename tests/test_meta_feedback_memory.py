from intelligence.meta.meta_memory import MetaMemory
from intelligence.meta.meta_feedback import MetaFeedbackRecord



def test_meta_memory_store():

    memory = MetaMemory()


    record = MetaFeedbackRecord(

        confidence_before=90,

        adjustment=-10,

        confidence_after=80,

        outcome="SUCCESS",

        meta_effective=True

    )


    memory.store(
        record
    )


    assert memory.count() == 1


    assert (
        memory.get_records()[0].outcome
        ==
        "SUCCESS"
    )