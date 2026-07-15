from dataclasses import dataclass


@dataclass
class ActionProposal:

    action: str
    status: str
    reason: str
    confidence: float