from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from guardian_core.cards.models import CardDrawResult
from guardian_core.intent.models import QuestionDNA
from guardian_core.spread.models import SpreadSelection


class ReadingSection(BaseModel):
    """Client-safe projection of one card's narrative section."""

    model_config = ConfigDict(extra="forbid")

    position: str = Field(min_length=1)
    card: str = Field(min_length=1)
    text: str = Field(min_length=1)


class ReadingResult(BaseModel):
    """The only reading-pipeline shape a client ever sees, embedded in ExperienceCommand.payload.

    Deliberately excludes question_dna, spread, draw, and reading_source: those are
    internal engine artifacts, not part of the World's client-facing contract.
    """

    model_config = ConfigDict(extra="forbid")

    contract_version: str = Field(default="1.0", pattern=r"^\d+\.\d+$")
    status: Literal["completed", "clarification_required"]
    reading_id: str | None = None
    central_message: str | None = None
    sections: list[ReadingSection] = Field(default_factory=list)
    reflection_question: str | None = None
    grounded_action: str | None = None
    closing: str | None = None
    clarification_question: str | None = None


@dataclass
class ReadingOutcome:
    """Internal, full-fidelity result of the Runtime Orchestrator. Never serialized to a client."""

    status: Literal["completed", "clarification_required"]
    question_dna: QuestionDNA
    spread: SpreadSelection | None
    draw: CardDrawResult | None
    reading: dict | None
    reading_source: Literal["ai", "template"] | None
    clarification_question: str | None
