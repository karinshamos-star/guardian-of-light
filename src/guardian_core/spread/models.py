from __future__ import annotations

from pydantic import BaseModel, Field

from guardian_core.intent.models import QuestionDNA


class SpreadPosition(BaseModel):
    id: str
    label: str
    purpose: str
    weight: float = Field(gt=0.0, le=2.0)


class SpreadDefinition(BaseModel):
    spread_id: str
    version: str = "1.0"
    name: str
    supported_needs: list[str]
    supported_complexities: list[str]
    positions: list[SpreadPosition]
    active: bool = True

    @property
    def card_count(self) -> int:
        return len(self.positions)


class SpreadSelectionRequest(BaseModel):
    question_dna: QuestionDNA
    available_spreads: list[SpreadDefinition] = Field(default_factory=list)
    user_preferences: dict = Field(default_factory=dict)


class SpreadSelection(BaseModel):
    spread_id: str
    spread_version: str
    reason: str
    positions: list[SpreadPosition]
    card_count: int = Field(ge=1, le=5)
    confidence: float = Field(ge=0.0, le=1.0)
