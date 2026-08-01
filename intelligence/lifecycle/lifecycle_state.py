from enum import Enum


class LifecycleState(Enum):

    CREATED = "CREATED"

    CANDIDATE = "CANDIDATE"

    ACTIVE = "ACTIVE"

    CHAMPION = "CHAMPION"

    RETIRED = "RETIRED"

    ARCHIVED = "ARCHIVED"