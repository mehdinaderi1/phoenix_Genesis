from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class StrategyVersion:

    name: str

    version: str = "v1"

    generation: int = 1

    parent_strategy: Optional[str] = None

    score: float = 0.0

    success_rate: float = 0.0

    status: str = "ACTIVE"

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


    def evolve(
        self,
        new_score: float,
        new_success_rate: float
    ):

        new_generation = self.generation + 1

        return StrategyVersion(

            name=f"{self.name}_v{new_generation}",

            version=f"v{new_generation}",

            generation=new_generation,

            parent_strategy=self.name,

            score=new_score,

            success_rate=new_success_rate,

            status="CANDIDATE"
        )


    def activate(self):

        self.status = "ACTIVE"


    def retire(self):

        self.status = "RETIRED"


    def archive(self):

        self.status = "ARCHIVED"


    def to_dict(self):

        return {

            "name": self.name,

            "version": self.version,

            "generation": self.generation,

            "parent_strategy": self.parent_strategy,

            "score": self.score,

            "success_rate": self.success_rate,

            "status": self.status,

            "created_at": self.created_at.isoformat()

        }