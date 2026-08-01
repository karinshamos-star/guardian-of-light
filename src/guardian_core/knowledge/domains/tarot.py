from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ..models import KnowledgeEntity
from .registry import DomainSchema, register_domain_schema


class CardArcana(StrEnum):
    MAJOR = "major"
    MINOR = "minor"
    COURT = "court"


class CardDimensions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    emotional: str
    mental: str
    relational: str
    practical: str
    spiritual: str


class CardContexts(BaseModel):
    model_config = ConfigDict(extra="forbid")

    love: str
    work: str
    money: str
    decision: str
    growth: str


class CardKnowledgeData(BaseModel):
    """Domain-specific payload for a tarot card -- merges the older, richer
    '12 -- Tarot Knowledge Schema' field set with the cross-tradition
    relation habit of the newer Notion 'Cards' database, resolving the
    two-schema duplication the audit flagged into one canonical shape."""

    model_config = ConfigDict(extra="forbid")

    arcana: CardArcana
    suit: str | None = None
    rank: str | None = None
    name_he: str
    core_essence: str
    light_expression: str
    shadow_expression: str
    reversed_expression: str
    dimensions: CardDimensions
    contexts: CardContexts
    reflection_questions: list[str] = Field(min_length=1)
    grounded_actions: list[str] = Field(min_length=1)
    safety_notes: str | None = None


class CardKnowledge(KnowledgeEntity):
    domain: Literal["tarot"] = "tarot"
    entity_type: Literal["card"] = "card"
    data: CardKnowledgeData


TAROT_CARD_SCHEMA = DomainSchema(
    domain="tarot",
    entity_type="card",
    current_version="1.0",
    model=CardKnowledge,
)

register_domain_schema(TAROT_CARD_SCHEMA)
